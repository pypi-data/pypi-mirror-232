import { DisposableDelegate, IDisposable } from '@lumino/disposable';
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ToolbarButton } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
  INotebookModel,
  NotebookActions,
  NotebookPanel
} from '@jupyterlab/notebook';
import { Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { Range } from 'react-date-range';
import { createPeriodCell, createTagHistoryCell } from './cells';
import { createOrUpdateCellById } from './utils/cells';
import CellId from './enums/CellId';
import { App } from './widgets/App';
import { DataToAdd, UserSettings } from './types';
import { addTagsIcon, dateRangeIcon, selectTagsFromPage } from './icons';

/**
 * The plugin registration information.
 */

const PLUGIN_ID = 'energy_machines_jupyter_reports:settings';
const plugin: JupyterFrontEndPlugin<void> = {
  requires: [ISettingRegistry],
  activate,
  id: PLUGIN_ID,
  autoStart: true
};

const updatePluginSettings = new Signal<any, UserSettings>({});

/**
 * A notebook widget extension that adds a button to the toolbar.
 */

// TODO parse currently opened notebook, to found hmi cells
export class ManageTagsWidget
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  settings: UserSettings;

  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    let toggleSelectTagsFromListDialog = new Signal<any, boolean>(this);
    let injectDataToNoteBook = new Signal<any, DataToAdd>(this);
    let toggleSetPeriodDialog = new Signal<any, boolean>(this);
    let setDateRange = new Signal<any, Range>(this);
    let toggleSelectTagsFromPageDialog = new Signal<any, boolean>(this);
    const notebook = panel.content;

    const app: App = new App(
      toggleSelectTagsFromListDialog,
      injectDataToNoteBook,
      toggleSetPeriodDialog,
      setDateRange,
      toggleSelectTagsFromPageDialog,
      updatePluginSettings
    );

    const selectTagsFromListCallback = (): void => {
      toggleSelectTagsFromListDialog.emit(true);
    };

    const selectTagsFromPageCallback = (): void => {
      toggleSelectTagsFromPageDialog.emit(true);
    };

    const notebookModel = context.model;

    // TODO work with notebook lifecycle
    // TODO code should be inject only after notebook is attached
    injectDataToNoteBook.connect((slot, dataToAdd) => {
      createOrUpdateCellById(
        notebookModel,
        createTagHistoryCell(notebookModel, dataToAdd, this.settings),
        CellId.HISTORY_REQUEST
      );
      NotebookActions.runAll(notebook, context.sessionContext);
    });

    setDateRange.connect((slot, range) => {
      createOrUpdateCellById(
        notebookModel,
        createPeriodCell(notebookModel, range),
        CellId.PERIOD
      );
      NotebookActions.runAll(notebook, context.sessionContext);
    });

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const selectTagsFromListButton = new ToolbarButton({
      icon: addTagsIcon,
      onClick: selectTagsFromListCallback,
      tooltip: 'Select tags from list'
    });

    const editOrSetPeriodButton = new ToolbarButton({
      icon: dateRangeIcon,
      onClick: (): void => {
        toggleSetPeriodDialog.emit(true);
      },
      tooltip: 'Edit or set period'
    });

    const selectTagsFromPageButton = new ToolbarButton({
      icon: selectTagsFromPage,
      onClick: selectTagsFromPageCallback,
      tooltip: 'Select tags from page'
    });

    Widget.attach(app, document.body);
    // TODO should to think about correct place to insert select tags button
    panel.toolbar.insertItem(
      0,
      'select-tags-from-page',
      selectTagsFromPageButton
    );
    panel.toolbar.insertItem(0, 'edit-or-set-period', editOrSetPeriodButton);
    panel.toolbar.insertItem(0, 'select-tags', selectTagsFromListButton);

    return new DisposableDelegate(() => {
      app.dispose();

      selectTagsFromListButton.dispose();
      editOrSetPeriodButton.dispose();
      selectTagsFromPageButton.dispose();

      toggleSelectTagsFromListDialog = null;
      injectDataToNoteBook = null;
      toggleSetPeriodDialog = null;
      setDateRange = null;
      toggleSelectTagsFromPageDialog = null;
    });
  }

  setSettings(settings: UserSettings): void {
    this.settings = settings;
  }
}

/**
 * Activate the extension.
 */

// TODO read more about notebook:INotebookTracker
function activate(app: JupyterFrontEnd, settings: ISettingRegistry): void {
  const widget = new ManageTagsWidget();

  app.docRegistry.addWidgetExtension('Notebook', widget);

  settings.pluginChanged.connect((settings, pluginId) => {
    if (pluginId === PLUGIN_ID) {
      settings.load(PLUGIN_ID).then(settings => {
        updatePluginSettings.emit({
          domain: (settings.get('domain').composite as string) || '',
          accessToken: (settings.get('accessToken').composite as string) || ''
        });
      });
    }
  });
  Promise.all([app.restored, settings.load(PLUGIN_ID)]).then(([, setting]) => {
    updatePluginSettings.emit({
      domain: (setting.get('domain').composite as string) || '',
      accessToken: (setting.get('accessToken').composite as string) || ''
    });
  });

  updatePluginSettings.connect((slot, settings) => {
    widget.setSettings(settings);
  });
}

/**
 * Export the plugin as default.
 */
export default plugin;
