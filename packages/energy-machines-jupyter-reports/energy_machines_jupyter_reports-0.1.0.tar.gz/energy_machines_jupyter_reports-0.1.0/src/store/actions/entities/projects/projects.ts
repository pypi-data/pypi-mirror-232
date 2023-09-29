import { isNil, sortBy } from 'lodash';
import { createFetchEntityAction } from '../../helpers';
import IProject from '../../../../interfaces/IProject';
import { projectsListSlice } from '../../../slices/entities/projectsList';
import { RootState } from '../../../reducers';
import { getProjectsList } from '../../../../api';

export const fetchProjectsList = createFetchEntityAction<IProject[]>({
  actions: projectsListSlice.actions,
  checkInCache: (state: RootState) => !isNil(state.projectsList.model),
  fetchEntity: getProjectsList,
  checkIsFetching: (state: RootState) => state.projectsList.isFetching,
  entityMapping: projects =>
    sortBy(projects, project => project.name.toLocaleLowerCase())
});
