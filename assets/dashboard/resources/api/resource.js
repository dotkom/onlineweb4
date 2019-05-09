import toQueryString from 'common/utils/queryParams';

const getAllResources = async (params = {}) => {
  const response = await fetch(`/api/v1/resources${toQueryString({ ...params, format: 'json', page_size: 60 })}`);
  const json = await response.json();
  return json.results || [];
};

export default getAllResources;
