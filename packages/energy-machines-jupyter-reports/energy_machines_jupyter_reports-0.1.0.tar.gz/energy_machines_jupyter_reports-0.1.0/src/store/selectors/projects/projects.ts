import { createSelector } from 'reselect';
import { RootState } from '../../reducers';
import IProject from '../../../interfaces/IProject';
import { matchNegativeWildcardRegex } from '../../../utils/filters';

export const makeGetFilteredProjects = () =>
  createSelector<RootState, string, IProject[], string, IProject[]>(
    state => state.projectsList.model,
    (_, query) => query,
    (projectsList, query) => {
      let projectsListItems: IProject[] = [];
      if (projectsList) {
        if (query) {
          const queryLowerCase = query.toLocaleLowerCase();
          projectsListItems = projectsList.filter(project => {
            // TODO also handle project type
            return matchNegativeWildcardRegex(project.name, queryLowerCase);
          });
        } else {
          projectsListItems = projectsList;
        }
      }

      return projectsListItems;
    }
  );

export const getFilteredProjects = makeGetFilteredProjects();
