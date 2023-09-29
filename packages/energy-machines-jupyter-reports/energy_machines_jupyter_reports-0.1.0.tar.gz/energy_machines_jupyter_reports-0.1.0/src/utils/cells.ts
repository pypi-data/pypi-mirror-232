import { INotebookModel } from '@jupyterlab/notebook';
import { ICodeCellModel } from '@jupyterlab/cells';
import CellId from '../enums/CellId';

export const createOrUpdateCellById = (
  notebookModel: INotebookModel,
  cell: ICodeCellModel,
  id: CellId
): void => {
  const cellsIterator = notebookModel.cells.iter();
  let currentCell = cellsIterator.next();
  let cellToUpdate: ICodeCellModel = null;
  let cellIndex = -1;
  let index = 0;
  while (currentCell) {
    if (currentCell.id === id) {
      cellToUpdate = currentCell as ICodeCellModel;
      cellIndex = index;
      break;
    }
    currentCell = cellsIterator.next();
    index++;
  }
  if (cellToUpdate) {
    notebookModel.cells.remove(cellIndex);
    notebookModel.cells.insert(cellIndex, cell);
  } else {
    if (id === CellId.PERIOD) {
      notebookModel.cells.insert(0, cell);
    } else {
      const cellsIterator = notebookModel.cells.iter();
      let currentCell = cellsIterator.next();
      let indexToAdd = 0;
      while (currentCell) {
        if (currentCell.id === CellId.PERIOD) {
          indexToAdd = 1;
          break;
        }
        currentCell = cellsIterator.next();
      }
      notebookModel.cells.insert(indexToAdd, cell);
    }
  }
};
