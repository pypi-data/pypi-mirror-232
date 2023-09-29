import { get } from '../base';
import ITag from '../../interfaces/ITag';

export async function getTagsListByProjectId(
  projectId: string
): Promise<ITag[]> {
  return get<ITag[]>(`${projectId}/tag/list`);
}
