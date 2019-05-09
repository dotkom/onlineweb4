/**
 * TODO: Add validation
 * @param {object} queryObject e.g. {foo: 'bar', hello: 'world'}
 * @return {string} e.g. ?foo=bar&hello=world
 */
const toQueryString = (queryObject) => {
  const keys = Object.keys(queryObject);
  if (!keys.length) {
    return '';
  }
  const queries = keys
    .filter(key => queryObject[key] !== undefined)
    .map(key => `${key}=${queryObject[key]}`);
  return `?${queries.join('&')}`;
};

export default toQueryString;
