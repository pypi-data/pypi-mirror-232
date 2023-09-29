import { INotebookModel } from '@jupyterlab/notebook';
import { ICodeCellModel } from '@jupyterlab/cells';
import { Range } from 'react-date-range';
import format from 'date-fns/format';
import { DataToAdd, UserSettings } from '../types';
import { createValidPythonVariable } from '../utils/python';
import { getDomain } from '../utils/settings';
import CellId from '../enums/CellId';
import { DATE_TIME_FORMAT } from '../utils/dateTimeFormat';

const createCellBySource = ({
  notebookModel,
  source,
  id
}: {
  notebookModel: INotebookModel;
  source: string[];
  id: string;
}): ICodeCellModel => {
  return notebookModel.contentFactory.createCodeCell({
    cell: {
      // eslint-disable-next-line @typescript-eslint/camelcase
      cell_type: 'code',
      source: source.join('\n'),
      metadata: {}
    },
    id
  });
};

export const createTagHistoryCell = (
  notebookModel: INotebookModel,
  data: DataToAdd,
  settings: UserSettings
): ICodeCellModel | null => {
  const { projects } = data;
  let cellToAdd: ICodeCellModel = null;

  if (projects.length) {
    const source = ['import requests'];
    source.push(
      `\nheaders = {'Content-Type': 'application/json','Authorization': 'Bearer ${settings.accessToken}' }`
    );
    const projectTagsVariables: {
      [projectId: string]: string[];
    } = {};
    projects.forEach(project => {
      const projectTagsPaths = data.tags[project.id];

      const projectTagsVariable = createValidPythonVariable(
        `${project.name}_tags_history`
      );

      source.push(`${projectTagsVariable} = requests.post('${`${getDomain()}/api/v1/`}${
        project.id
      }/history/aggregate/by-path/json', headers=headers, json = {
        "groupingType": "MINUTES",
        "tagList": [${projectTagsPaths.map(path => `'${path}'`)}],
        "timeFrom": time_from,
        "timeTo": time_to
      }).json()`);
      projectTagsVariables[project.id] = projectTagsPaths.map(
        (tagPath, index) => {
          return `${createValidPythonVariable(
            `${project.name}_${tagPath}_history`
          )} = ${projectTagsVariable}[${[index]}]`;
        }
      );
    });
    projects.forEach(project => {
      source.push(`\n# ${project.name} tags history variables`);
      projectTagsVariables[project.id].forEach(variables =>
        source.push(variables)
      );
    });
    cellToAdd = createCellBySource({
      notebookModel,
      source,
      id: CellId.HISTORY_REQUEST
    });
  }

  return cellToAdd;
};

export const createPeriodCell = (
  notebookModel: INotebookModel,
  { startDate, endDate }: Range
): ICodeCellModel | null => {
  const source = [];
  source.push(
    `time_from = ${startDate.valueOf()} # ${format(
      startDate,
      DATE_TIME_FORMAT
    )}`
  );
  source.push(
    `time_to = ${endDate.valueOf()} # ${format(endDate, DATE_TIME_FORMAT)}`
  );

  return createCellBySource({
    notebookModel,
    source,
    id: CellId.PERIOD
  });
};
