/**
 * Created by myth on 3/9/16.
 */

var GalleryUpload = (function ($, Dropzone) {
  // DOM references
  var UPLOAD_PANE = $('#gallery__upload-pane')

  return {
    /**
     * Initialize the GalleryUpload module
     */
    init: function () {
      // Fetch unhandled images on dropzone upload queue complete
      if (UPLOAD_PANE.length) {
        // Sadly, since the Dropzone instance event bind (.on()) did not work, and dynamic generation of Dropzones
        // without the class="dropzone" attribute fails to append the dropzone class, we must use the autoDiscover
        // aproach, but disable the autodiscover, so we get the styling, while being able to hook into onqueuecomplete
        // event.
        Dropzone.autoDiscover = false

        // Transform the upload form to a dropzone instance
        return new Dropzone('#gallery__image-upload-form', {
          action: '/gallery/upload',
          clickable: true,
          init: function (e) {
            this.on('queuecomplete', function (e) {
              Gallery.events.fire('gallery-newUnhandledImage')
            })
          }
        })
      }
    }
  }
})(window.jQuery, window.Dropzone)

var GalleryCrop = (function ($, Cropper) {
  var _cropper

  // DOM References
  var MANAGE_BUTTON = $('#gallery__edit-button')
  var MANAGE_PANE = $('#gallery__manage-pane')

  return {
    /**
     * Initialize the GalleryCrop module
     */
    init: function () {
      // Check if we are rendering the manage-pane directly
      if (MANAGE_PANE.length && window.location.href.indexOf('#gallery__manage-pane') !== -1) {
        MANAGE_BUTTON.click()
      }
    },

    /**
     * Opens the image crop and manage view, given some image data
     * @param {object} img An object containing at least an image ID, and full original size url
     */
    manage: function (img) {
      var imageDOM = $('<img></img>')
      var imageData = Gallery.images.get(img)

      imageDOM.attr({
        'src': imageData.image,
        'id': 'gallery__image-active'
      })

      $('#gallery__image-edit-container').html(imageDOM)
      // Cropperjs sadly fails if provided a jQuery wrapped DOM Node in the constructor...
      var image = document.getElementById('gallery__image-active')
      _cropper = new Cropper(image, {
        aspectRatio: 16 / 9
      })
    }
  }
})(window.jQuery, window.Cropper)

var Gallery = (function ($, Utils, MicroEvent, Dropzone) {
  var _events = new MicroEvent()
  var _images = {}

  // DOM references
  var MANAGE_BUTTON_TEXT = $('#gallery__manage-button-text')
  var THUMBNAIL_VIEW = $('#gallery__thumbnail-view')

  /**
   * Set up AJAX such that Django receives its much needed CSRF token
   */
  var doAjaxSetup = function () {
    /**
     * Checks whether an HTTP method is considered CSRF safe or not
     * @param {string} method An HTTP method as string
     * @returns {boolean} true if the provided HTTP method is CSRF-safe. False otherwise.
     */
    var csrfSafeMethod = function (method) {
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method.toUpperCase()))
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
      var imgLink = $('<a></a>').html(img)
      var imageID = images[i].id

      img.attr({
        'class': 'gallery__unhandled-image',
        'data-id': imageID,
        'src': images[i].thumbnail
      })
      imgLink.attr({
        'data-toggle': 'tab',
        'href': '#gallery__edit-pane',
        'role': 'tab'
      })

      THUMBNAIL_VIEW.append(imgLink)

      // Add event listener
      img.on('click', function (e) {
        GalleryCrop.manage($(this).attr('data-id'))
      })
    }
  }

  /**
   * Retrieve an array of all UnhandledImage objects currently in the database
   */
  var fetchUnhandledImages = function () {
    var success = function (images) {
      // Update the local image cache with current data
      images = images.unhandled
      for (var i = 0; i < images.length; i++) {
        _images[images[i].id] = images[i]
      }

      // Update the manage button text and create thumbnails for the manage unhandled images view
      MANAGE_BUTTON_TEXT.text('Behandle ({0})'.format(images.length))
      createUnhandledImageThumbnails(images)
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

      // Initialize the support modules
      GalleryCrop.init()
      GalleryUpload.init()
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
    },

    /**
     * The images submodule exposes helper methods for accessing the images
     */
    images: {
      /**
       * Retrieve the image with the provided ID.
       * @param {number} id The ID (in the database (primary key)) the image is stored with
       * @returns {*} An object containing basic unhandled image data (id, thumb_url and orig_url)
       */
      get: function (id) {
        return _images[id]
      }
    }
  }
})(window.jQuery, window.Utils, window.MicroEvent, window.Dropzone)

// Initialise the Gallery module
Gallery.init()
