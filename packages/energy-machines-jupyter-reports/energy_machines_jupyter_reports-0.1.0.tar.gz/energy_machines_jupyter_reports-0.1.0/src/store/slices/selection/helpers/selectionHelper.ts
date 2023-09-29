import { createSlice } from '@reduxjs/toolkit';

type MapType = {
  [id: string]: string;
};

export type SelectionModel = {
  selectedIds: MapType;
  isAllSelected: boolean;
  deselectedIds: MapType;
};

export const createSelectionSlice = (selectionName: string) => {
  const initialState: SelectionModel = {
    selectedIds: {},
    isAllSelected: false,
    deselectedIds: {}
  };

  return createSlice({
    name: selectionName,
    initialState,
    reducers: {
      setSelected(state, action) {
        state.selectedIds = action.payload;
      },
      setSelectAll(state, action) {
        state.isAllSelected = action.payload;
        state.selectedIds = {};
        state.deselectedIds = {};
      },
      setDeselected(state, action) {
        state.deselectedIds = action.payload;
      }
    }
  });
};
