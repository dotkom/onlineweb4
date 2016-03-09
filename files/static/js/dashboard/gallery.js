/**
 * Created by myth on 10/24/15.
 */

var GalleryDashboard = (function ($, tools) {

    /* Private fields */

    var SEARCH_ENDPOINT = '/api/v1/images/'
    var search_field, search_button, result_table, years, tags

    years = $('.dashboard-gallery-year')
    tags = $('.dashboard-gallery-tag')
    search_field = $('#dashboard-gallery-search-query')
    search_button = $('#dashboard-gallery-search-button')
    result_table = $('#dashboard-gallery-table')

    /* Private functions */

    /**
     * Generic API helper function that only takes on an URI
     * @param uri Relative URI on the endpoint
     */
    var doRequest = function (uri) {
        last_request = uri

        var success = function (data) {
            GalleryDashboard.draw(data)
        }
        var error = function (xhr, statusText, thrownError) {
            tools.showStatusMessage('Det oppstod en uventet feil: ' + xhr.responseText, 'alert-danger')
        }
        // Trigger AJAX request with query
        tools.ajax('GET', uri, null, success, error, 'json')
    }

    /* Public API */
    return {
        /**
         * Initializes the Gallery Dashboard Module by binding event listeners
         * to search field, button and years filters.
         */
        init: function () {
            search_field.on('keypress', function (e) {
                if (e.keyCode === 13) {
                    e.preventDefault()
                    e.stopPropagation()
                    GalleryDashboard.search($(this).val())
                }
            })

            search_button.on('click', function(e) {
                e.preventDefault()
                GalleryDashboard.search(search_field.val())
            })

            years.on('click', function (e) {
                e.preventDefault()
                GalleryDashboard.filter($(this).text())
            })

            tags.on('click', function (e) {
                e.preventDefault();
                GalleryDashboard.search($(this).text())
            })
        },

        /**
         * Perform a text query search by using the ResponsiveImage API
         * @param query: A search query as text
         */
        search: function (query) {
            doRequest(SEARCH_ENDPOINT + '?query=' + query)
        },

        /**
         * Perform a filter search on a year by using the ResponsiveImage API
         * @param year: A year filter as text
         */
        filter: function (year) {
            doRequest(SEARCH_ENDPOINT + '?year=' + year)
        },

        /**
         * Render a list of search results by providing the returned results
         * from a ResponsiveImage API call.
         * @param data: A JSON object result in Django REST Framework format
         */
        draw: function (data) {
            var html = '';

            if (!data.results.length) html = '<tr><td colspan="4">Ingen bilder matchet søket...</td></tr>'
            else {
                for (var i = 0; i < data.results.length; i++) {
                    var t = moment(data.results[i].timestamp)

                    html += '<tr><td>'
                    html +=   '<a href="' + data.results[i].id + '/">'
                    html +=     '<img src="' + data.results[i].thumb + '" alt title="' + data.results[i].name + '">'
                    html += '</a></td><td>'
                    html +=   '<a href="' + data.results[i].id + '/">' + data.results[i].name + '</a>'
                    html += '</td><td>'
                    html +=   data.results[i].description
                    html += '</td><td>'
                    html +=   t.format('YYYY-MM-DD HH:MM:SS')
                    html += '</td></tr>'
                }
            }
            result_table.html(html)
        }
    }
})(jQuery, Dashboard.tools)

GalleryDashboard.init()
