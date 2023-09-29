import { get } from '../base';
import IVendorPagesTree from '../../interfaces/IVendorPagesTree';

export async function getPagesTree(
  projectId: string
): Promise<IVendorPagesTree> {
  return get<IVendorPagesTree>(`${projectId}/page/tree`);
}
