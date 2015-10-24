/**
 * Created by myth on 10/24/15.
 */

var Gallery = (function ($, tools) {
    /* Private fields */

    years = $('.dashboard-gallery-year')
    search_field = $('#dashboard-gallery-search-query')
    search_button = $('#dashboard-gallery-search-button')
    result_table = $('#dashboard-gallery-table')


    /* Private functions */

    // Performs an image search and draws the results in the result table
    var searchImages = function (query) {
        payload = { query: query }
        tools.ajax('GET', '/gallery/search/', payload, function (data) {
            var html = '';
            for (var i = 0; i < data.images.length; i++) {

                html += '<div class="col-md-6 col-sm-12 col-xs-12">'
                html +=   '<div class="image-selection-thumbnail" data-id="' + data.images[i].id + '">'
                html +=     '<div class="image-selection-thumbnail-image">'
                html +=       '<img src="' + data.images[i].thumbnail + '" title="' + data.images[i].name + '">'
                html +=     '</div>'
                html +=     '<div class="image-selection-thumbnail-text">'
                html +=       '<h4 class="image-title">' + data.images[i].name + '</h4>'
                html +=       '<span class="image-timestamp">' + data.images[i].timestamp + '</span>'
                html +=       '<p class="image-description">' + data.images[i].description +'</p>'
                html +=     '</div>'
                html +=   '</div>'
                html += '</div>'
            }
            if (!data.images.length) html = '<div class="col-md-12"><p>Ingen bilder matchet søket...</p></div></div>'
            else html += '</div>'
            result_table.html(html)

        }, function (xhr, thrownError, statusText) {
            alert(thrownError)
        })
    }

    /* Public API */
    return {
        init: function () {
            search_field.on('keypress', function (e) {
                if (e.keyCode === 13) {
                    e.preventDefault();
                    e.stopPropagation();
                    searchImages($(this).val())
                }
            })

            search_button.on('click', function(e) {
                e.preventDefault()
                searchImages(search_field.val())
            })

            years.on('click', function (e) {
                e.preventDefault()
                searchImages($(this).text())
            })
        }
    }
})(jQuery, Dashboard.tools)

Gallery.init()
