import { loadCityFromZipCode } from 'common/utils/';
import { DependentDocumentation } from './dependent_fields';
import enableUserSearch from './userSearch';
import './profiles';
import './less/profiles.less';

const zipCodeElement = document.getElementById('zip-code');
if (zipCodeElement) {
  const cityElement = document.getElementById('city');
  loadCityFromZipCode(zipCodeElement, cityElement);
}

const userSearchElement = document.getElementById('user-search');
if (userSearchElement) {
  enableUserSearch();
}
DependentDocumentation();
