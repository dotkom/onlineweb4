/**
 * Created by myth on 3/9/16.
 */

var GalleryUpload = (function () {
    return {
        /**
         * Initialize the GalleryUpload module
         */
        init: function () {
            // TODO: Maek stuff happen
        }
    }
})()

var GalleryCrop = (function () {
    return {
        /**
         * Initialize the GalleryCrop module
         */
        init: function () {
            // TODO: Maek stuff happen
        }
    }
})

var Gallery = (function ($) {
    var _timers = []
    var _events = new MicroEvent()

    // DOM references
    var MANAGE_BUTTON = $('#dashboard-gallery__manage-button-text')
    var MANAGE_PANE = $('#dashboard-gallery__manage-pane')
    var UPLOAD_PANE = $('#dashboard-gallery__upload-pane')

    /**
     * Set up AJAX such that Django receives its much needed CSRF token
     */
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

    /**
     * Retrieve an array of all UnhandledImage objects currently in the database
     */
    var fetchUnhandledImages = function () {
        var success = function (images) {
            MANAGE_BUTTON.text('Behandle ({0})'.format(images.unhandled.length))
            console.log(images)
        }
        var error = function (xhr, errorMessage, responseText) {
            console.log('Received error: ' + xhr.responseText + ' ' + errorMessage)
        }

        // Fetch all unhandled images from the Gallery endpoint
        Gallery.ajax('GET', '/gallery/unhandled/', null, success, error, null)
    }

    return {
        /**
         * Initialize the Gallery module.
         */
        init: function () {
            // Do the ajax setup
            doAjaxSetup()

            // Register retrieval of unhandled images on the newUnhandledImage event
            this.events.on('gallery-newUnhandledImage', fetchUnhandledImages)

            // Fire an initial "newUnhandledImage" event
            this.events.fire('gallery-newUnhandledImage')
        },

        /**
         * Perform an AJAX request of type "method" to "url" with the optional "data", specified
         * "success" and "error" callback functions, and optional data "type" specification.
         * @param {string} method The HTTP method
         * @param {string} url The url of the endpoint to send the request to
         * @param {object} data An optional object literal of data (can be null)
         * @param {function} success A success callback function that must accept one data argument
         * @param {function} error An error callback function that must accept xhr, thrownError and responseText args
         * @param {string} type An optional data type specification
         */
        ajax: function (method, url, data, success, error, type) {
            var payload = {
                type: method.toUpperCase(),
                url: url,
                success: success,
                error: error
            }
            if (data !== null || data !== undefined) payload.data = data
            if (type !== null || type !== undefined) {
                if (type === 'json') {
                    payload.contentType = 'application/json; charset=UTF-8'
                    payload.dataType = 'json'
                }
            }
            $.ajax(payload)
        },

        /**
         * The events submodule faciliatates event listener registry and event dispatching
         */
        events: {
            /**
             * Tells the event system to fire an event of the given type.
             * @param {string} event
             */
            fire: function (event) {
                _events.fire(event)
            },

            /**
             * Register a callback function on events of the given type.
             * @param {string} event
             * @param {function} callback
             */
            on: function (event, callback) {
                _events.on(event, callback)
            }
        }
    }
})(jQuery)

// Initialise the Gallery module
Gallery.init()
