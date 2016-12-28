import { loadCityFromZipCode } from 'common/utils/';

const zipCodeElement = document.getElementById('zip-code');
if (zipCodeElement) {
  const cityElement = document.getElementById('city');
  loadCityFromZipCode(zipCodeElement, cityElement);
}
