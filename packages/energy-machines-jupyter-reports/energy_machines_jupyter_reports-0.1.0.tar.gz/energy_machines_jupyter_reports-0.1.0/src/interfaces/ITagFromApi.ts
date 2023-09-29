import IWithId from './IWithId';

export default interface ITagFromApi extends IWithId {
  path: string;
  isWritable: boolean;
  unit: string;
}
