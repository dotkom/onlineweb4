import toQueryString from 'common/utils/queryParams';

const getAllHobbies = async (params = {}) => {
  const response = await fetch(`/api/v1/hobbys${toQueryString({ ...params, format: 'json', page_size: 60 })}`);
  const json = await response.json();
  return json.results || [];
};

export default getAllHobbies;
