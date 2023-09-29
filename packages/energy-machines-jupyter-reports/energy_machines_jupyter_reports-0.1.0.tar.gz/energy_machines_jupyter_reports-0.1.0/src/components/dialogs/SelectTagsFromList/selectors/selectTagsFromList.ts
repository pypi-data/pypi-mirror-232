import { createSelectorCreator, defaultMemoize } from 'reselect';
import { get, find, isEqual } from 'lodash';
import { RootState } from '../../../../store/reducers';
import ITag from '../../../../interfaces/ITag';
import IProject from '../../../../interfaces/IProject';
import { matchNegativeWildcardRegex } from '../../../../utils/filters';

type Params = {
  projectsIds: string[];
  query: string;
};

export interface ITagTableItem extends ITag {
  projectName: string;
}

type ProjectsMap = {
  [projectId: string]: IProject;
};

const createDeepEqualSelector = createSelectorCreator(defaultMemoize, isEqual);

export const getTagsListItems = createDeepEqualSelector<
  RootState,
  Params,
  ITag[],
  string,
  ProjectsMap,
  ITagTableItem[]
>(
  (state, { projectsIds }) => {
    const tags: ITag[] = [];
    projectsIds.forEach(projectId => {
      const tagsByProject = get(state.tagsList, [projectId, 'model']);
      if (tagsByProject) {
        tags.push(...tagsByProject);
      }
    });
    return tags;
  },
  (_, { query }) => query.toLowerCase(),
  (state, { projectsIds }) => {
    const projectsById: ProjectsMap = {};
    const projects = state.projectsList.model;
    projectsIds.forEach(projectId => {
      projectsById[projectId] = find(projects, {
        id: projectId
      });
    });
    return projectsById;
  },
  (tagsList, query, projectsMap) => {
    const tableItems: ITagTableItem[] = [];

    tagsList.forEach(tag => {
      if (matchNegativeWildcardRegex(tag.path, query)) {
        if (tag.path) {
          tableItems.push({
            ...tag,
            projectName: projectsMap[tag.projectId].name
          });
        }
      }
    });
    return tableItems;
  }
);
