import { get } from '../base';
import IProject from '../../interfaces/IProject';

export async function getProjectById(projectId: string): Promise<IProject> {
  return get<IProject>(`${projectId}/project`);
}

export async function getProjectsList(): Promise<IProject[]> {
  return get<IProject[]>('projects/list');
}
