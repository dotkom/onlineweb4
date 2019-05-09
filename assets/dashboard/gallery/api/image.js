import toQueryString from 'common/utils/queryParams';

const getResponsiveImages = async (params = {}) => {
  const response = await fetch(`/api/v1/images/${toQueryString(params)}`);
  const json = await response.json();
  return json.results || [];
};

export default getResponsiveImages;
