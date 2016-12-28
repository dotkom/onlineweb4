import { template } from 'underscore';
import { cityFromZipCode } from './request';

/**
 * Render a template on the basis of the attributes of a data object
 * @param {object} tmpl A jQuery wrapper DOM object
 * @param {object} context An object containing the template payload
 * @return {object} Rendered DOM subtree containing provided context data
 */
export const render = (tmpl, context) => {
  const node = template(tmpl);
  return node(context);
};

/**
 * Helper function to add city after zip code
 * @param {HTMLElement} zipCode Element containing zip code
 * @param {HTMLElement} city Element where city should be stored
 */
export const loadCityFromZipCode = (zipCodeElement, cityElement) => {
  const zipCode = zipCodeElement.textContent;
  cityFromZipCode(zipCode).then((city) => {
    // TODO: Look into a cleaner way to do this
    // eslint-disable-next-line no-param-reassign
    cityElement.innerHTML = `&nbsp;${city}`;
  });
};
