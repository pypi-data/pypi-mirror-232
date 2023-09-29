import { createSelectionSlice } from '../helpers';
import { TAGS_LIST } from '../../../constants';

export const selectedTagsSlice = createSelectionSlice(TAGS_LIST);
