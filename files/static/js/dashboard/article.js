/**
 * Created by myth on 10/18/15.
 */

var Article = (function ($, tools) {
    // Private fields and methods

    var SEARCH_ENDPOINT = '/api/v1/articles/'

    var page, query, searchButton, results, paginator, years;

    /**
     * Generic API helper function that only takes on an URI
     * @param uri Relative URI on the endpoint
     */
    var doRequest = function (uri) {
        last_request = uri

        var success = function (data) {
            Article.table.draw(data)
        }
        var error = function (xhr, statusText, thrownError) {
            tools.showStatusMessage('Det oppstod en uventet feil: ' + statusText, 'alert-danger')
        }
        // Trigger AJAX request with query
        tools.ajax('GET', uri, null, success, error, 'json')
    }

    // Public fields
    return {
        init: function () {

            page = 1
            query = $('#dashboard-article-search-query')
            searchButton = $('#dashboard-article-search-button')
            results = $('#dashboard-article-table')
            years = $('.dashboard-article-year')
            tagform = $('#dashboard-article-inline-tag-form')

            // Bind click listener for search button
            searchButton.on('click', function (e) {
                e.preventDefault()
                Article.search(query.val())
            })

            // Listen for enter key press
            query.on('keypress', function (e) {
                if (e.keyCode === 13) {
                    Article.search(query.val())
                }
            })

            // Bind click listener to year filter buttons
            years.on('click', function (e) {
                e.preventDefault()
                Article.filter($(this).text())
            })

            // Intercept inline tag form posting and update tags list
            $('#article-inline-tag-submit').on('click', function (e) {
                e.preventDefault()
                $.ajax({
                    method: 'POST',
                    url: '/dashboard/article/tag/new/',
                    data: tagform.serialize(),
                    success: function (data) {
                        $('#article-inline-tag-error').hide()
                        $('#id_tags').append('<option value="' + data.id + '">' + data.name + '</option>')
                        $('#article-tag-name').val('')
                        $('#article-tag-slug').val('')
                    },
                    error: function (xhr, statusText, thrownError) {
                        $('#article-inline-tag-error').text('Klarte ikke legge til ny tag: ' + statusText).show()
                    }
                })
            })
        },

        search: function (query) {
            doRequest(SEARCH_ENDPOINT + '?query=' + query)
        },

        filter: function (year) {
            doRequest(SEARCH_ENDPOINT + '?year=' + year)
        },

        table: {
            draw: function (items) {
                var html = ''
                for (var i = 0; i < items.results.length; i++) {
                    var item = items.results[i]
                    var t = moment(item.published_date)

                    html += '<tr>'
                    html += '<td><a href="' + item.id + '">' + item.heading + '</a></td>'
                    html += '<td>' + item.author.first_name + ' ' + item.author.last_name + '</td>'
                    html += '<td>' + t.format('YYYY-MM-DD HH:MM:SS') + '</td>'
                    html += '<td><a href="/dashboard/article/' + item.id + '/edit/">'
                    html += '<i class="fa fa-edit fa-lg"></i></a></td></tr>'
                }

                results.html(html)

                // TODO: Pagination
            }
        }
    }
})(jQuery, Dashboard.tools)

Article.init()
