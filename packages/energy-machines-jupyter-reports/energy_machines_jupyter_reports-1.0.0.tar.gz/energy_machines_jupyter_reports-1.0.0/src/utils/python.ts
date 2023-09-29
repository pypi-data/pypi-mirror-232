export const createValidPythonVariable = (s: string): string => {
  return s.replace(/(\.|\s|\/|-)/g, '_');
};
