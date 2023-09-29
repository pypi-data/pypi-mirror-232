import IVendorMetadataTree from './IVendorMetadataTree';
import PageType from '../enums/PageType';

export default interface IPagesTree
  extends IVendorMetadataTree<IPagesTree, PageType> {
  path: string;
}
