import jQuery from 'jquery';
import moment from 'moment';

/**
 * Created by myth on 10/24/15.
 */

const GalleryDashboard = (function PrivateGalleryDashboard($, tools) {
  /* Private fields */

  const SEARCH_ENDPOINT = '/api/v1/images/';

  const years = $('.dashboard-gallery-year');
  const tags = $('.dashboard-gallery-tag');
  const searchField = $('#dashboard-gallery-search-query');
  const searchButton = $('#dashboard-gallery-search-button');
  const resultTable = $('#dashboard-gallery-table');

  /* Private functions */

  /**
   * Generic API helper function that only takes on an URI
   * @param uri Relative URI on the endpoint
   */
  const doRequest = (uri) => {
    const success = (data) => {
      GalleryDashboard.draw(data);
    };
    const error = (xhr) => {
      tools.showStatusMessage(`Det oppstod en uventet feil: ${xhr.responseText}`, 'alert-danger');
    };
    // Trigger AJAX request with query
    tools.ajax('GET', uri, null, success, error, 'json');
  };

  /* Public API */
  return {
    /**
     * Initializes the Gallery Dashboard Module by binding event listeners
     * to search field, button and years filters.
     */
    init() {
      searchField.on('keypress', function searchFieldKeyPress(e) {
        if (e.keyCode === 13) {
          e.preventDefault();
          e.stopPropagation();
          GalleryDashboard.search($(this).val());
        }
      });

      searchButton.on('click', (e) => {
        e.preventDefault();
        GalleryDashboard.search(searchField.val());
      });

      years.on('click', function clickYears(e) {
        e.preventDefault();
        GalleryDashboard.filter($(this).text());
      });

      tags.on('click', function tagClick(e) {
        e.preventDefault();
        GalleryDashboard.search($(this).text());
      });
    },

    /**
     * Perform a text query search by using the ResponsiveImage API
     * @param query: A search query as text
     */
    search(query) {
      doRequest(`${SEARCH_ENDPOINT}?query=${query}`);
    },

    /**
     * Perform a filter search on a year by using the ResponsiveImage API
     * @param year: A year filter as text
     */
    filter(year) {
      doRequest(`${SEARCH_ENDPOINT}?year=${year}`);
    },

    /**
     * Render a list of search results by providing the returned results
     * from a ResponsiveImage API call.
     * @param data: A JSON object result in Django REST Framework format
     */
    draw(data) {
      let html = '';

      if (!data.results.length) {
        html = '<tr><td colspan="4">Ingen bilder matchet søket...</td></tr>';
      } else {
        for (let i = 0; i < data.results.length; i += 1) {
          const timestamp = moment(data.results[i].timestamp);

          html += `
            <tr>
              <td>
                <a href="${data.results[i].id}/">
                  <img src="${data.results[i].thumb}" alt title="${data.results[i].name}">
                </a>
              </td>
              <td>
                <a href="${data.results[i].id}/">${data.results[i].name}</a>
              </td>
              <td>${data.results[i].description}</td>
              <td>${timestamp.format('YYYY-MM-DD HH:MM:SS')}</td>
            </tr>`;
        }
      }
      resultTable.html(html);
    },
  };
}(jQuery, window.Dashboard.tools));

export default GalleryDashboard;
