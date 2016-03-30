/**
 * Created by myth on 3/9/16.
 */

var GalleryUpload = (function ($) {
  return {
    /**
     * Initialize the GalleryUpload module
     */
    init: function () {
      // TODO: Maek stuff happen
    }
  }
})(window.jQuery)

var GalleryCrop = (function ($) {
  return {
    /**
     * Initialize the GalleryCrop module
     */
    init: function () {
      // TODO: Maek stuff happen
    }
  }
})(window.jQuery)

var Gallery = (function ($, Utils, MicroEvent, Dropzone) {
  var _events = new MicroEvent()

  // DOM references
  var MANAGE_BUTTON_TEXT = $('#gallery__manage-button-text')
  var MANAGE_BUTTON = $('#gallery__edit-button')
  var MANAGE_PANE = $('#gallery__manage-pane')
  var UPLOAD_FORM = $('#gallery__image-upload-form')
  var UPLOAD_PANE = $('#gallery__upload-pane')
  var THUMBNAIL_VIEW = $('#gallery__thumbnail-view')

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
          xhr.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'))
        }
      }
    })
  }

  /**
   * Create the HTML wrapper for the thumbnail of an UnhandledImage wrapper as a jQuery DOM object.
   * @param {object} image A JavaScript object containing id, link to original image as well as link to thumbnail
   */
  var createUnhandledImageThumbnails = function (images) {
    // Clear the unhandled image thumbnail view
    THUMBNAIL_VIEW.html('')

    // Add each thumbnail and bind event listener
    for (var i = 0; i < images.length; i++) {
      var img = $('<img></img>')
      img.attr({
        'class': 'gallery__unhandled-image',
        'data-id': images[i].id,
        'src': images[i].thumbnail
      })
      THUMBNAIL_VIEW.append(img)

      // Add event listener
      img.on('click', function (e) {
        console.log('Clicked image {0}'.format(img))
      })
    }
  }

  /**
   * Retrieve an array of all UnhandledImage objects currently in the database
   */
  var fetchUnhandledImages = function () {
    var success = function (images) {
      MANAGE_BUTTON_TEXT.text('Behandle ({0})'.format(images.unhandled.length))
      createUnhandledImageThumbnails(images.unhandled)
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

      // Check if we are rendering the manage-pane directly
      if (MANAGE_PANE.length && window.location.href.indexOf('#gallery__manage-pane') !== -1) {
        MANAGE_BUTTON.click()
      }

      // Fetch unhandled images on dropzone upload queue complete
      if (UPLOAD_PANE.length) {
        Dropzone.options.galleryImageUploadForm = {
          init: function () {
            this.on('queuecomplete', function (e) {
              fetchUnhandledImages()
            })
          }
        }
      }
    },

    /**
     * Perform an AJAX request of type "method" to "url" with the optional "data", specified
     * "success" and "error" callback functions, and optional data "type" specification.
     * @param {string} method The HTTP method
     * @param {string} url The url of the endpoint to send the request to
     * @param {object} data An optional object literal of data (can be null)
     * @param {function} success A success callback function that must accept one data argument
     * @param {function} error An error callback function that must accept xhr, thrownError and responseText args
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
})(window.jQuery, window.Utils, window.MicroEvent, window.Dropzone)

// Initialise the Gallery module
Gallery.init()
