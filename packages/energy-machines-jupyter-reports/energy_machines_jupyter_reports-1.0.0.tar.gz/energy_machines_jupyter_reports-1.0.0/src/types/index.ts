type TagsPaths = string[];
import IProject from '../interfaces/IProject';

export type DataToAdd = {
  projects: IProject[];
  tags: {
    [projectId: string]: TagsPaths;
  };
};

export type UserSettings = {
  accessToken: string;
  domain: string;
};
