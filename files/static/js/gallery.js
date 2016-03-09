/**
 * Created by myth on 3/9/16.
 */

var GalleryUpload = (function () {
    /*
     * Private methods
     */

    /*
     * Private methods
     */

    /*
     * Private methods
     */
    return {
        // Initialize the GalleryUpload module
        init: function () {
            // TODO: Maek stuff happen
        }
    }
})()

var GalleryCrop = (function () {
    /*
     * Private methods
     */

    /*
     * Private methods
     */

    /*
     * Private methods
     */
    return {
        // Initialize the GalleryCrop module
        init: function () {
            // TODO: Maek stuff happen
        }
    }
})

var Gallery = (function ($) {
    /*
     * Private methods
     */


    /*
     * Private methods
     */

    /*
     * Private methods
     */

    // Ajax setup
    var doAjaxSetup = function () {
        var csrfSafeMethod = function (method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
        }

        $.ajaxSetup({
            crossDomain: false,
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'))
                }
            }
        })
    }

    // Retrieves an array of all the UnhandledImage instances in the database
    var fetchUnhandledImages = function () {
        var error = function (xhr, )

    }

    /*
     * Private methods
     */
    return {
        // Initialize the Gallery module
        init: function () {
            // TODO: Maek stuff happen
        }
    }
})(jQuery)
