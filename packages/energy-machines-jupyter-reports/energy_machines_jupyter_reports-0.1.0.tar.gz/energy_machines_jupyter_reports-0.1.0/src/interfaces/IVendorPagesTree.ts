import IVendorMetadataTree from './IVendorMetadataTree';
import PageType from '../enums/PageType';

// eslint-disable-next-line
export default interface IVendorPagesTree
  extends IVendorMetadataTree<IVendorPagesTree, PageType> {}
