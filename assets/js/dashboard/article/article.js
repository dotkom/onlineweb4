import moment from 'moment';
/**
 * Created by myth on 10/18/15.
 */

/*
  TODO duvholt: PrivateArticle is a bit weird.
  Can't be Article since then Article.search will refer
  to the function itself instead of the returned object
*/
const Article = (function PrivateArticle($, tools) {
    // Private fields and methods

  const SEARCH_ENDPOINT = '/api/v1/articles/';

  let query;
  let searchButton;
  let results;
  let years;
  let tags;

    /**
     * Generic API helper function that only takes on an URI
     * @param uri Relative URI on the endpoint
     */
  const doRequest = function doRequest(uri) {
    const success = function success(data) {
      Article.table.draw(data);
    };
    const error = function error(xhr, statusText) {
      tools.showStatusMessage(`Det oppstod en uventet feil: ${statusText}`, 'alert-danger');
    };
        // Trigger AJAX request with query
    tools.ajax('GET', uri, null, success, error, 'json');
  };

    // Public fields
  return {
    init() {
      query = $('#dashboard-article-search-query');
      searchButton = $('#dashboard-article-search-button');
      results = $('#dashboard-article-table');
      years = $('.dashboard-article-year');
      tags = $('.dashboard-article-tag');

            // Bind click listener for search button
      searchButton.on('click', (e) => {
        e.preventDefault();
        Article.search(query.val());
      });

            // Listen for enter key press
      query.on('keypress', (e) => {
        if (e.keyCode === 13) {
          Article.search(query.val());
        }
      });

            // Bind click listener to year filter buttons
      years.on('click', function yearClick(e) {
        e.preventDefault();
        Article.filter($(this).text());
      });

            // Bind click listener to tags filter buttons
      tags.on('click', function tagClick(e) {
        e.preventDefault();
        Article.tags($(this).text());
      });
    },

    search(searchQuery) {
      doRequest(`${SEARCH_ENDPOINT}?query=${searchQuery}`);
    },

    filter(year) {
      doRequest(`${SEARCH_ENDPOINT}?year=${year}`);
    },

    tags(tag) {
      doRequest(`${SEARCH_ENDPOINT}?tags=${tag}`);
    },

    table: {
      draw(items) {
        let html = '';
        for (let i = 0; i < items.results.length; i += 1) {
          const item = items.results[i];
          const t = moment(item.published_date);

          html += '<tr>';
          html += `<td><a href="${item.id}">${item.heading}</a></td>`;
          html += `<td>${item.authors}</td>`;
          html += `<td>${t.format('YYYY-MM-DD HH:MM:SS')}</td>`;
          html += `<td><a href="/dashboard/article/${item.id}/edit/">`;
          html += '<i class="fa fa-edit fa-lg"></i></a></td></tr>';
        }

        results.html(html);

                // TODO: Pagination
      },
    },
  };
}(jQuery, window.Dashboard.tools));

Article.init();
