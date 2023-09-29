import { PAGES_TREE } from '../../../constants';
import { createEntityByPathSlice } from '../helpers';
import IPagesTree from '../../../../interfaces/IPagesTree';

export default createEntityByPathSlice<IPagesTree>(PAGES_TREE, action => {
  const { args } = action.meta;
  const [projectId] = args;
  return projectId;
});
