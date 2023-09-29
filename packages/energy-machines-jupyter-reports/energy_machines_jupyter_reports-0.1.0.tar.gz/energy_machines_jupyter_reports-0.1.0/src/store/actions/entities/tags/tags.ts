import { isNil, get } from 'lodash';
import { createFetchEntityAction } from '../../helpers';
import ITag from '../../../../interfaces/ITag';
import ITagFromApi from '../../../../interfaces/ITagFromApi';
import { tagsListSlice } from '../../../slices/entities';
import { getTagsListByProjectId } from '../../../../api';
import { RootState } from '../../../reducers';

export const fetchTagsListByProjectId = createFetchEntityAction<
  ITagFromApi[],
  ITag[]
>({
  actions: tagsListSlice.actions,
  checkInCache: (state: RootState, projectId: string) =>
    !isNil(get(state, ['tagsList', projectId, 'model'])),
  fetchEntity: async (projectId: string) => getTagsListByProjectId(projectId),
  checkIsFetching: (state: RootState, projectId: string) =>
    get(state, ['tagsList', projectId, 'isFetching'], false),
  entityMapping: (tags, projectId: string) =>
    tags.map(tag => ({
      ...tag,
      id: tag.id + projectId,
      projectId,
      tagId: tag.id
    }))
});
