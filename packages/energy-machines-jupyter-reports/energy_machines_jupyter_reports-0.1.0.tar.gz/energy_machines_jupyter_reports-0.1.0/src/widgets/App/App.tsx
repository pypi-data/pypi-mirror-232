import React from 'react';
import { ReactWidget, UseSignal } from '@jupyterlab/apputils';
import { Signal } from '@lumino/signaling';
import { Range } from 'react-date-range';
import { App as AppComponent } from '../../components/App';
import { DataToAdd, UserSettings } from '../../types';

export default class App extends ReactWidget {
  constructor(
    private toggleSelectTagsFromListDialogSignal: Signal<any, boolean>,
    private injectDataToNoteBookSignal: Signal<any, DataToAdd>,
    private toggleSetPeriodDialog: Signal<any, boolean>,
    private setDateRangeSignal: Signal<any, Range>,
    private toggleSelectTagsFromPageDialogSignal: Signal<any, boolean>,
    private updateUserSettingsSignal: Signal<any, UserSettings>
  ) {
    super();
  }

  onInFinishButtonClick = (data: DataToAdd): void => {
    this.injectDataToNoteBookSignal.emit(data);
    this.toggleSelectTagsFromListDialogSignal.emit(false);
  };

  onDateRangeChange = (range: Range): void => {
    this.setDateRangeSignal.emit(range);
    this.toggleSetPeriodDialog.emit(false);
  };

  onCloseSelectTagsFromListDialog = (): void => {
    this.toggleSelectTagsFromListDialogSignal.emit(false);
  };

  onCloseSetPeriodDialog = (): void => {
    return this.toggleSetPeriodDialog.emit(false);
  };

  onCloseSelectTagsFromPageDialog = (): void => {
    this.toggleSelectTagsFromPageDialogSignal.emit(false);
  };

  render(): JSX.Element {
    return (
      <UseSignal
        signal={this.toggleSelectTagsFromListDialogSignal}
        initialArgs={false}
      >
        {(sender, isSelectTagsFromListDialogOpen) => {
          return (
            <UseSignal signal={this.toggleSetPeriodDialog} initialArgs={false}>
              {(setPeriodSend, isSetPeriodDialogOpen) => (
                <UseSignal
                  signal={this.toggleSelectTagsFromPageDialogSignal}
                  initialArgs={false}
                >
                  {(sender, isSelectTagsFromPageDialogOpen) => {
                    return (
                      <UseSignal signal={this.updateUserSettingsSignal}>
                        {(sender, userSettings) => (
                          <AppComponent
                            isSelectTagsFromListDialogOpen={
                              isSelectTagsFromListDialogOpen
                            }
                            isSelectTagsFromPageDialogOpen={
                              isSelectTagsFromPageDialogOpen
                            }
                            isSetPeriodDialogOpen={isSetPeriodDialogOpen}
                            userSettings={userSettings}
                            onFinishButtonClick={this.onInFinishButtonClick}
                            onCloseSelectTagsFromListDialog={
                              this.onCloseSelectTagsFromListDialog
                            }
                            onCloseSetPeriodDialog={this.onCloseSetPeriodDialog}
                            onDateRangeChange={this.onDateRangeChange}
                            onCloseSelectTagsFromPageDialog={
                              this.onCloseSelectTagsFromPageDialog
                            }
                          />
                        )}
                      </UseSignal>
                    );
                  }}
                </UseSignal>
              )}
            </UseSignal>
          );
        }}
      </UseSignal>
    );
  }
}
