import Bloodhound from 'corejs-typeahead/dist/bloodhound';
import "corejs-typeahead/dist/typeahead.jquery";
import "corejs-typeahead/dist/typeahead.bundle";

import Urls from 'common/utils/django_reverse';
import { template } from 'underscore';
import './less/typeahead.less';

/**
 * Simple wrapper function for Typeahead
 * @param {Object} element jQuery element to apply typeahead to
 * @params {Object} options Options for typeahead (template, url, select, display)
 * Template has to be compiled. e.g. _.template('<div>...</div>')
 */
export const typeahead = (element, options) => {
  const source = new Bloodhound({
    // Boilerplate
    datumTokenizer(d) {
      return Bloodhound.tokenizers.whitespace(d.num);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: options.url,
      wildcard: '%QUERY',
    },
  });
  element.typeahead({
    valueKey: 'id',
  }, {
    name: options.name || 'typeahead',
    source,
    templates: {
      suggestion: options.template,
    },
    display: options.display || 'name',
  }).on('typeahead:selected typeahead:autocompleted', options.select);
};

export const plainUserTypeahead = (element, select) => {
  const plainUserSearchTemplate = template(`
    <span data-id="<%= id %>" class="user-meta"><h4><%= value %></h4>
  `);

  typeahead(element, {
    template: plainUserSearchTemplate,
    url: `${Urls.profiles_api_plain_user_search()}?query=%QUERY`,
    select,
    display: 'value',
    name: 'users-plain',
  });
};

export { typeahead as default };
