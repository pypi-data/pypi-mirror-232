import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { EntityStateShape } from './types';
import userSettingsSlice from '../../userSettings';

export function createEntitySlice<T>(entityName: string) {
  const initialState: EntityStateShape<T> = {
    model: null,
    isFetching: false,
    hasBeenFetched: false,
    isFetchingError: false,
    needToInvalidate: false,
    error: null
  };
  return createSlice({
    name: entityName,
    initialState,
    reducers: {
      fetchEntityStart(state): void {
        state.model = null;
        state.isFetching = true;
        state.error = null;
        state.hasBeenFetched = false;
        state.needToInvalidate = false;
      },
      fetchEntitySuccess(state, action): void {
        state.model = action.payload;
        state.isFetching = false;
        state.error = null;
        state.hasBeenFetched = true;
        state.needToInvalidate = false;
      },
      fetchEntityFailure(state, action: PayloadAction<string>): void {
        state.isFetching = false;
        state.error = action.payload;
        state.hasBeenFetched = true;
        state.needToInvalidate = false;
      }
    },
    extraReducers: {
      [userSettingsSlice.actions.setAccessToken.type]: () => initialState
    }
  });
}
