import $ from 'jquery';
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

export const toggleChecked = (element) => {
  const checkedIcon = 'fa-check-square-o';
  const uncheckedIcon = 'fa-square-o';
  const allITags = $(element).find('i');
  const ilen = allITags.length;

  let icon;
  for (let m = 0; m < ilen; m += 1) {
    icon = allITags[m];
    if ($(icon).hasClass('checked')) {
      $(icon).removeClass('checked').removeClass(checkedIcon).addClass(uncheckedIcon);
    } else {
      $(icon).addClass('checked').removeClass(uncheckedIcon).addClass(checkedIcon);
    }
  }
};
