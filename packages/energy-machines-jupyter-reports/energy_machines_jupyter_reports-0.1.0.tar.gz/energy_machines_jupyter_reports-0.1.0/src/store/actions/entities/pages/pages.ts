import { get, isNil, last, sortBy } from 'lodash';
import { createFetchEntityAction } from '../../helpers';
import IPagesTree from '../../../../interfaces/IPagesTree';
import { pagesTreeSlice } from '../../../slices/entities/pagesTree';
import { RootState } from '../../../reducers';
import { getPagesTree } from '../../../../api';
import IVendorPagesTree from '../../../../interfaces/IVendorPagesTree';

const vendorTreeToPagesTree = (tree: IVendorPagesTree): IPagesTree => {
  return {
    ...tree,
    path: '',
    children: tree.children.map(vendorTreeToPagesTree)
  };
};

export const fetchPagesTree = createFetchEntityAction<
  IVendorPagesTree,
  IPagesTree
>({
  actions: pagesTreeSlice.actions,
  checkInCache: (state: RootState, projectId) =>
    !isNil(get(state, ['pagesTree', projectId, 'model'])),
  fetchEntity: async projectId => getPagesTree(projectId),
  checkIsFetching: (state: RootState, projectId) =>
    get(state, ['pagesTree', projectId, 'isFetching'], false),
  entityMapping: (vendorPagesTree): IPagesTree => {
    const pagesTree = vendorTreeToPagesTree(vendorPagesTree);
    const parentTree: IPagesTree[] = [];

    const trees = [pagesTree];

    while (trees.length) {
      const tree = trees.pop();
      tree.children = sortBy(
        get(tree, 'children', []),
        subTree => subTree.type,
        subTree => subTree.name.toLowerCase()
      );

      while (parentTree.length) {
        const lastParent = last(parentTree);
        if (lastParent.id !== tree.parentId) {
          parentTree.pop();
        } else {
          break;
        }
      }

      const path = parentTree
        .slice(1)
        .map(t => t.name)
        .join('/');
      tree.path = path === '' ? tree.name : `${path}/${tree.name}`;

      if (get(tree, ['children', 'length'], 0)) {
        parentTree.push(tree);
      }

      trees.push(...tree.children);
    }

    return pagesTree;
  }
});
