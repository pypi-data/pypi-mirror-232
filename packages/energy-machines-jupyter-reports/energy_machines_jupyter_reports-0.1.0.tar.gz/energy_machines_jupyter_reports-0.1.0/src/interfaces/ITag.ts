import ITagFromApi from './ITagFromApi';

export default interface ITag extends ITagFromApi {
  projectId: string;
  tagId: string;
}
