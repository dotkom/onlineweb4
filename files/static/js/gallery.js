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
  var self = this

  // DOM References
  var EDIT_CONTAINER = $('#gallery__image-edit-container')
  var IMAGE_LOG = $('#gallery__image-edit--log')
  var IMAGE_PRESET = $('#gallery__image-edit--preset')
  var IMAGE_HEIGHT = $('#gallery__image-edit--height')
  var IMAGE_WIDTH = $('#gallery__image-edit--width')
  var IMAGE_ZOOM_IN = $('#gallery__image-edit__zoom-in')
  var IMAGE_ZOOM_OUT = $('#gallery__image-edit__zoom-out')
  var IMAGE_SET_CROP_MODE = $('#gallery__image-edit__crop')
  var IMAGE_SET_DRAG_MODE = $('#gallery__image-edit__drag')
  var IMAGE_RESET = $('#gallery__image-edit__reset')
  var MANAGE_BUTTON = $('#gallery__edit-button')
  var MANAGE_PANE = $('#gallery__manage-pane')
  var PREVIEW_IMAGE = $('#gallery__image-edit--preview')

  // Cropper
  self.cropper = null
  self.options = {
    aspectRatio: 16 / 9,
    preview: '#gallery__image-edit--preview-wrapper',
    autoCrop: true,
    dragCrop: true,
    viewMode: 2,
    movable: true,
    resizable: true,
    zoomable: true,
    rotatable: false,
    multiple: false,
    cropmove: function (event) {
      $('#gallery__image-edit--width').val(self.cropper.getData(true).width)
      $('#gallery__image-edit--height').val(self.cropper.getData(true).height)

      // TODO: Apply validation function that checks lower height and width bounds with respect to
      // the currently active preset
    }
  }

  /**
   * Updates the cropper object options
   */
  var updateCropperOptions = function (preset) {
    switch (preset) {
      case '1':
        self.cropper.setAspectRatio(16 / 9)
        break
      case '2':
        self.cropper.setAspectRatio(19 / 7)
        break
      case '3':
        self.cropper.setAspectRatio(NaN)
        break
      case '4':
        self.cropper.setAspectRatio(2 / 3)
        break
      case '5':
        self.cropper.setAspectRatio(NaN)
        break
    }

    // Update sidebar with new aspect ratio data
    var cropData = self.cropper.getData(true)
    IMAGE_HEIGHT.val(cropData.height)
    IMAGE_WIDTH.val(cropData.width)
  }

  /**
   * Binds all necessary event listeners for the GalleryCrop module
   */
  var bindEventListeners = function () {
    console.log('Setting up GalleryCrop event listeners ...')

    // Listen for changes to selected preset
    IMAGE_PRESET.on('change', function (e) {
      var preset = $(this).children('option:selected').val()
      updateCropperOptions(preset)
    })

    // Zoom in
    IMAGE_ZOOM_IN.on('click', function (e) {
      self.cropper.zoom(0.1)
    })

    // Zoom out
    IMAGE_ZOOM_OUT.on('click', function (e) {
      self.cropper.zoom(-0.1)
    })

    // Activates crop selection tool
    IMAGE_SET_CROP_MODE.on('click', function (e) {
      self.cropper.setDragMode('crop')
    })

    // Activates mouse move tool
    IMAGE_SET_DRAG_MODE.on('click', function (e) {
      self.cropper.setDragMode('move')
    })

    // Reset the selection
    IMAGE_RESET.on('click', function (e) {
      self.cropper.clear()
    })

    // Listen for changes directly to the height field
    IMAGE_HEIGHT.on('keyup', function (e) {
      var imageData = self.cropper.getData(true)
      imageData.height = Number(IMAGE_HEIGHT.val())
      self.cropper.setData(imageData)
    })

    // Listen for changes directly to the width field
    IMAGE_WIDTH.on('keyup', function (e) {
      var imageData = self.cropper.getData(true)
      imageData.width = Number(IMAGE_WIDTH.val())
      self.cropper.setData(imageData)
    })
  }

  return {
    /**
     * Initialize the GalleryCrop module
     */
    init: function () {
      // Check if we are rendering the manage-pane directly
      if (MANAGE_PANE.length && window.location.href.indexOf('#gallery__manage-pane') !== -1) {
        MANAGE_BUTTON.click()
      }

      // If we see the image crop preset selection dropdown, we are in edit mode and can safely bind the crop
      // event listeners.
      if (IMAGE_PRESET.length > 0) {
        bindEventListeners()
      }
    },

    /**
     * Prints a log message to the log field in the right hand sidebar of the edit image view
     * @param {string} msg The message to be displayed
     */
    log: function (msg) {
      IMAGE_LOG.text(msg)
    },

    /**
     * Opens the image crop and manage view, given some image data
     * @param {object} img An object containing at least an image ID, and full original size url
     */
    manage: function (img) {
      var imageData = Gallery.images.get(img)
      var image = new window.Image()
      image.id = 'gallery__image-active'
      image.src = imageData.image

      EDIT_CONTAINER.html(image)
      PREVIEW_IMAGE.attr({'src': imageData.image})

      // For reasons still unknown, cropper needs a timeout before being able to wrap the img.
      // Hooking the wrapper to the img load event does not work.
      setTimeout(function () {
        if (self.cropper !== null && self.cropper !== undefined) self.cropper.destroy()
        self.cropper = new Cropper(image, self.options)

        var cropData = self.cropper.getData()
        IMAGE_HEIGHT.val(cropData.height)
        IMAGE_WIDTH.val(cropData.width)

        GalleryCrop.log('Klar til bruk')
      }, 500)
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
