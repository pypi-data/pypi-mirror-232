import IWithId from './IWithId';

export default interface IVendorMetadataTree<
  C extends IVendorMetadataTree<C, T>,
  T
> extends IWithId {
  projectId: string;
  name: string;
  id: string;
  parentId: string | null;
  type: T;
  children: C[];
}
