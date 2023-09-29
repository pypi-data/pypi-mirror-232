export const getWildCardSearchRegex: (query: string) => RegExp = (
  query = ''
) => {
  return new RegExp(
    '' +
      query
        .replace(/\\/g, '\\\\')
        .replace(/\./g, '\\.')
        .replace(/\?/g, '.')
        .replace(/\*+/g, '.*'),
    'i'
  );
};

export const matchNegativeWildcardRegex: (
  stringToCompare: string,
  query: string
) => boolean = (stringToCompare, query) => {
  if (query && stringToCompare) {
    if (query.startsWith('!')) {
      const searchQuery = query.slice(1);
      if (searchQuery) {
        return !stringToCompare.match(getWildCardSearchRegex(query.slice(1)));
      }
      return true;
    }
    return !!stringToCompare.match(getWildCardSearchRegex(query));
  }
  return true;
};
