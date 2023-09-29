import { TAGS_LIST } from '../../../constants';
import { createEntityByPathSlice } from '../helpers';
import ITag from '../../../../interfaces/ITag';

export default createEntityByPathSlice<ITag[]>(TAGS_LIST, action => {
  const { args } = action.meta;
  const [projectId] = args;
  return projectId;
});
