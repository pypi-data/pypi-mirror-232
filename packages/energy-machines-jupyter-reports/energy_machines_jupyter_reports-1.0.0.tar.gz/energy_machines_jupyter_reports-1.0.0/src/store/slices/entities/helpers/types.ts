export type EntityStateShape<T> = {
  model: null | T;
  isFetching: boolean;
  hasBeenFetched: boolean;
  needToInvalidate: boolean;
  isFetchingError: boolean;
  error: string | null;
};
