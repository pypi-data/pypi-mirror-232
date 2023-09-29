import { combineReducers } from '@reduxjs/toolkit';
import {
  projectsListSlice,
  tagsListSlice,
  pagesTreeSlice
} from '../slices/entities';
import {
  selectedTagsSlice,
  selectedProjectsSlice,
  selectedPagesSlice
} from '../slices/selection';
import dateRangeSlice from '../slices/dateRange';
import userSettingsSlice from '../slices/userSettings';

const rootReducer = combineReducers({
  projectsList: projectsListSlice.reducer,
  tagsList: tagsListSlice.reducer,
  selectedTags: selectedTagsSlice.reducer,
  selectedProjects: selectedProjectsSlice.reducer,
  selectedPages: selectedPagesSlice.reducer,
  dateRange: dateRangeSlice.reducer,
  pagesTree: pagesTreeSlice.reducer,
  userSettings: userSettingsSlice.reducer
});

export type RootState = ReturnType<typeof rootReducer>;
export type SelectionActionsType = typeof selectedTagsSlice.actions;

export default rootReducer;
