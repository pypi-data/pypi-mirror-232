import { set } from 'lodash';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { EntityStateShape } from './types';
import userSettingsSlice from '../../userSettings/userSettings';

type InitialStateType<T> = {
  [key: string]: EntityStateShape<T>;
};

export function createEntityByPathSlice<T>(
  entityName: string,
  getPath: (...args: any[]) => string
) {
  const initialState: InitialStateType<T> = {};
  return createSlice({
    name: entityName,
    initialState,
    reducers: {
      fetchEntityStart(state, action) {
        set(state, getPath(action), {});
        state[getPath(action)].model = null;
        state[getPath(action)].isFetching = true;
        state[getPath(action)].error = null;
        state[getPath(action)].hasBeenFetched = false;
        state[getPath(action)].needToInvalidate = false;
      },
      fetchEntitySuccess(state, action) {
        state[getPath(action)].model = action.payload;
        state[getPath(action)].isFetching = false;
        state[getPath(action)].error = null;
        state[getPath(action)].hasBeenFetched = true;
        state[getPath(action)].needToInvalidate = false;
      },
      fetchEntityFailure(state, action: PayloadAction<string>) {
        state[getPath(action)].isFetching = false;
        state[getPath(action)].error = action.payload;
        state[getPath(action)].hasBeenFetched = true;
        state[getPath(action)].needToInvalidate = false;
      }
    },
    extraReducers: {
      [userSettingsSlice.actions.setAccessToken.type]: (): InitialStateType<
        T
      > => initialState
    }
  });
}
