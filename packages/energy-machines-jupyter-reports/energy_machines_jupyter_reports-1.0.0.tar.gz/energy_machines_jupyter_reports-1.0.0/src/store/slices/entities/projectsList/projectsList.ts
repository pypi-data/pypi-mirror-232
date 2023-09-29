import { PROJECTS_LIST } from '../../../constants';
import { createEntitySlice } from '../helpers';
import IProject from '../../../../interfaces/IProject';

export default createEntitySlice<IProject[]>(PROJECTS_LIST);
