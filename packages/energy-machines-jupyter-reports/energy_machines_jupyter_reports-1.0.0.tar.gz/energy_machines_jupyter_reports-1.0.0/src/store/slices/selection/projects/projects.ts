import { createSelectionSlice } from '../helpers';
import { PROJECTS_LIST } from '../../../constants';

export const selectedProjectsSlice = createSelectionSlice(PROJECTS_LIST);
