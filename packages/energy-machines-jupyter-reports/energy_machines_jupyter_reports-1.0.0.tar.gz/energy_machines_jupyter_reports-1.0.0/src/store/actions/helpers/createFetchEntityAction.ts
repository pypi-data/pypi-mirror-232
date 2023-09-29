import { AppThunk } from '../../';
import { RootState } from '../../reducers';

type ArgumentsType<T, U> = {
  actions: any;
  fetchEntity: (...args: any[]) => Promise<T>;
  checkInCache: (state: RootState, ...other: any[]) => boolean;
  checkIsFetching: (state: RootState, ...other: any[]) => boolean;
  entityMapping?: (entity: T, ...args: any) => T | U;
};

export function createFetchEntityAction<T, U = T>({
  actions,
  fetchEntity,
  checkInCache,
  checkIsFetching,
  entityMapping = (entity: T, ...args: any): T => entity
}: ArgumentsType<T, U>) {
  return (...args: any): AppThunk => async (dispatch, getState) => {
    const state = getState();
    if (!checkIsFetching(state, ...args) && !checkInCache(state, ...args)) {
      dispatch({ ...actions.fetchEntityStart(), meta: { args } });
      try {
        const data: T = await fetchEntity(...args);
        dispatch({
          ...actions.fetchEntitySuccess(entityMapping(data, ...args)),
          meta: { args }
        });
      } catch (e) {
        dispatch({
          ...actions.fetchEntityFailure(e.toString()),
          meta: { args }
        });
      }
    }
  };
}
