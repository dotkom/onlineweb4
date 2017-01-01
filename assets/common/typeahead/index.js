import Bloodhound from 'corejs-typeahead';
import Urls from 'urls';
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
    name: 'user-profiles',
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
  });
};

export const userTypeahead = (element, select) => {
  const userSearchTemplate = template(`
    <div>
      <img width="100%" src="<%= image %>" alt="" />
      <span data-id="<%= id %>" class="user-meta"><h4><%= name %></h4>
    </div>
  `);

  typeahead(element, {
    template: userSearchTemplate,
    url: `${Urls.profiles_api_user_search()}?query=%QUERY`,
    select,
  });
};

export { typeahead as default };
