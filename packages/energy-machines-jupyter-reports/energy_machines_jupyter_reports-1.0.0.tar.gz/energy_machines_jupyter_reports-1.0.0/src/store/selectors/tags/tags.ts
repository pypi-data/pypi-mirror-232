import { get } from 'lodash';
import { createSelector } from 'reselect';
import { RootState } from '../../reducers';
import ITag from '../../../interfaces/ITag';
import { matchNegativeWildcardRegex } from '../../../utils/filters';

type Params = {
  projectId: string;
  query: string;
};

export const makeGetFilteredTagsList = () =>
  createSelector<RootState, Params, ITag[], string, ITag[]>(
    (state, { projectId }) => get(state, ['tagsList', projectId, 'model']),
    (_, { query }) => query,
    (tagsList, query) => {
      let tagsItems: ITag[] = [];
      if (tagsList) {
        if (query) {
          const queryLowerCase = query.toLocaleLowerCase();
          tagsItems = tagsList.filter(tag => {
            return matchNegativeWildcardRegex(tag.path, queryLowerCase);
          });
        } else {
          tagsItems = tagsList;
        }
      }
      return tagsItems;
    }
  );
