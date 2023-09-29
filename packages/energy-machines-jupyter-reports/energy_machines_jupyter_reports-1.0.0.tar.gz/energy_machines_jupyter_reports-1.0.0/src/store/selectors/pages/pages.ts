import { createSelector } from 'reselect';
import { get, last } from 'lodash';
import { RootState } from '../../reducers';
import IPagesTree from '../../../interfaces/IPagesTree';
import { matchNegativeWildcardRegex } from '../../../utils/filters';
import PageType from '../../../enums/PageType';

type Params = {
  projectId: string;
  query: string;
};

export const makeGetFilteredPages = () =>
  createSelector<RootState, Params, IPagesTree, string, IPagesTree>(
    (state, { projectId }) =>
      get(state, ['pagesTree', projectId, 'model'], null),
    (state, { query }) => query,
    (pagesTree, query) => {
      if (!pagesTree) {
        return null;
      }
      if (query === '') {
        return pagesTree;
      }

      const trees = [pagesTree];
      const resultTree: IPagesTree = { ...pagesTree, children: [] };
      const resultTrees = [resultTree];
      const parents: IPagesTree[] = [];

      while (trees.length) {
        const tree = trees.pop();
        const resultTree = resultTrees.pop();

        while (parents.length && last(parents).id !== tree.parentId) {
          parents.pop();
        }
        if (tree.children.length) {
          parents.push(resultTree);
        }

        tree.children.forEach(node => {
          if (node.type === PageType.Folder) {
            if (node.children.length) {
              trees.push(node);
              resultTree.children.push({ ...node, children: [] });
            }
          } else if (matchNegativeWildcardRegex(node.path, query)) {
            trees.push(node);
            resultTree.children.push({ ...node, children: [] });
          }
        });
        if (
          resultTree.type === PageType.Folder &&
          !resultTree.children.length
        ) {
          let nodeToFilter = resultTree;
          for (let i = parents.length - 1; i >= 0; i--) {
            parents[i].children = parents[i].children.filter(
              child => child !== nodeToFilter
            );
            if (parents[i].children.length) {
              break;
            }
            nodeToFilter = parents[i];
          }
        }

        resultTrees.push(...resultTree.children);
      }

      return resultTree;
    }
  );

export const getFilteredPages = makeGetFilteredPages();
