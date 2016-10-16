/**
 * Created by myth on 3/9/16.
 */

const TMPL_IMAGE_SEARCH_RESULT = `
<% for (var image of images) { %>
<div class="col-md-6 col-sm-12 col-xs-12">
 <div class="image-selection-thumbnail" data-id="<%= image.id %>">
  <div class="image-selection-thumbnail-image">
   <img src="<%= image.thumbnail %>" title="<%= image.name %>">
  </div>
  <div class="image-selection-thumbnail-text">
    <h4 class="image-title"><%= image.name %></h4>
    <span class="image-timestamp"><%= image.timestamp %></span>
    <p class="image-description"><%= image.description %></p>
  </div>
 </div>
</div>
<% } %>`

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

var GalleryCrop = (function ($, Cropper, utils) {
  var self = this

  // DOM References
  var CROP_IMAGE = $('#gallery__image-edit--submit')
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
  var IMAGE_DESCRIPTION = $('#gallery__image-edit--description')
  var IMAGE_NAME = $('#gallery__image-edit--name')
  var IMAGE_PHOTOGRAPHER = $('#gallery__image-edit--photographer')
  var IMAGE_TAGS = $('#gallery__image-edit--tags')
  var MANAGE_BUTTON = $('#gallery__edit-button')
  var MANAGE_PANE = $('#gallery__manage-pane')
  var MODAL_CROPFAILED = $('#gallery__image-edit__crop-failed')
  var MODAL_PROCESSING = $('#gallery__image-edit__processing')
  var MODAL_SUCCESS = $('#gallery__image-edit__crop-success')
  var RESET_BUTTON = $('#gallery__image-edit__back')
  var PREVIEW_IMAGE = $('#gallery__image-edit--preview')

  // Cropper
  self.cropper = null
  self.imageId = -1
  self.presets = {}
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
      var cropData = self.cropper.getData(true)

      $('#gallery__image-edit--width').val(cropData.width)
      $('#gallery__image-edit--height').val(cropData.height)

      // Since we just moved the crop window, we need to inform stuff that listens for image data changes
      Gallery.events.fire('gallery-imageDataChanged')
    }
  }

  /**
   * Binds all necessary event listeners for the GalleryCrop module
   */
  var bindEventListeners = function () {
    console.log('Setting up GalleryCrop event listeners ...')

    // Zoom in
    IMAGE_ZOOM_IN.on('click', function (e) {
      self.cropper.zoom(0.1)
      Gallery.events.fire('gallery-imageDataChanged')
    })

    // Zoom out
    IMAGE_ZOOM_OUT.on('click', function (e) {
      self.cropper.zoom(-0.1)
      Gallery.events.fire('gallery-imageDataChanged')
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
      Gallery.events.fire('gallery-imageDataChanged')
    })

    // Listen for changes directly to the width field
    IMAGE_WIDTH.on('keyup', function (e) {
      var imageData = self.cropper.getData(true)
      imageData.width = Number(IMAGE_WIDTH.val())
      self.cropper.setData(imageData)
      Gallery.events.fire('gallery-imageDataChanged')
    })

    IMAGE_NAME.on('keyup', function (e) {
      Gallery.events.fire('gallery-imageDataChanged')
    })

    IMAGE_DESCRIPTION.on('keyup', function (e) {
      Gallery.events.fire('gallery-imageDataChanged')
    })

    // Listen for crop button click event
    CROP_IMAGE.on('click', function (e) {
      e.preventDefault()
      GalleryCrop.crop(self.presets[IMAGE_PRESET.children('option:selected').val()])
    })

    // Listen for changes to image data, so we can perform necessary tasks like sanity checks / validation
    Gallery.events.on('gallery-imageDataChanged', function () {
      GalleryCrop.validate(self.presets[IMAGE_PRESET.children('option:selected').val()])
    })

    // Hop back to the unhandled image thumbnail preview on crop success
    Gallery.events.on('gallery-imageCropSuccessful', function (e, data) {
      MODAL_PROCESSING.modal('hide')
      RESET_BUTTON.click()
      GalleryCrop.reset()

      var _tmpl = '<p>Bilde {0} ({1}) av type "{2}" ble beskåret uten problemer</p>'.format(
        data.name, data.id, data.preset
      )
      MODAL_SUCCESS.find('.modal-body').html(_tmpl)
      MODAL_SUCCESS.modal('show')

      // Fire the newUnhandledImage event, as it will force a reload of the server side state
      Gallery.events.fire('gallery-newUnhandledImage')
    })

    // Handle crop failure events
    Gallery.events.on('gallery-imageCropFailed', function (e) {
      MODAL_PROCESSING.modal('hide')
      MODAL_CROPFAILED.modal('show')
    })
  }

  /**
   * Retrieves the list of available presets from the server via an AJAX request.
   */
  var getCropPresetsFromServer = function () {
    IMAGE_LOG.text('Henter preset fra tjeneren...')
    console.log('Fetching crop presets from server')

    // Declare success callback
    var success = function (data) {
      // Update the select dropdown
      IMAGE_PRESET.html('')
      var optionTemplate = '<option value="<%= val %>" <%= selected %>><%= description %></option>'
      for (var i = 0; i < data.presets.length; i++) {
        var name = data.presets[i].name
        self.presets[name] = data.presets[i]
        var context = {
          val: name,
          description: data.presets[i].description
        }
        if (i === 0) context.selected = 'selected'
        else context.selected = ''

        IMAGE_PRESET.append(utils.render(optionTemplate, context))
      }

      // Listen for changes to selected preset
      IMAGE_PRESET.on('change', function (e) {
        var preset = $(this).children('option:selected').val()
        GalleryCrop.preset(preset)
      })
    }

    // Declare error callback
    var error = function (xhr, errorMessage, responseText) {
      IMAGE_LOG.text('En feil har oppstått')
      console.error(responseText)
    }

    Gallery.ajax('GET', '/gallery/preset/', null, success, error, null)
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
        // Presets are defined in the Gallery app settings file
        getCropPresetsFromServer()
      }
    },

    /**
     * Performs a validation check before sending a POST request to the backend with the current cropData.
     * @param {object} preset A preset object containing attributes such as min_width, aspect_ratio etc.
     */
    crop: function (preset) {
      var _errors = GalleryCrop.validate(preset)

      // Fire cropFailed and return prematurely if errors exist
      if (_errors.length > 0) return Gallery.events.fire('gallery-imageCropFailed')

      // Prepare the image crop data payload with necessary fields
      var payload = self.cropper.getData(true)
      payload.id = Number(self.imageId)
      payload.name = IMAGE_NAME.val()
      payload.description = IMAGE_DESCRIPTION.val()
      payload.photographer = IMAGE_PHOTOGRAPHER.val() || ''
      payload.preset = IMAGE_PRESET.children(':selected').val()
      payload.tags = IMAGE_TAGS.val() || ''

      // Declare the success callback
      var _success = function (data) {
        data.name = payload.name
        data.preset = payload.preset
        Gallery.events.fire('gallery-imageCropSuccessful', data)
      }
      // Declare the error callback
      var _error = function (xhr, errorMessage, responseText) {
        Gallery.events.fire('gallery-imageCropFailed')
        console.error('Received error: ' + xhr.responseText + ' ' + errorMessage)
      }

      // Lock user out from GUI
      MODAL_PROCESSING.modal('show')

      Gallery.ajax('POST', '/gallery/crop/', payload, _success, _error)
    },

    /**
     * Prints a log message to the log field in the right hand sidebar of the edit image view
     * @param {string} msg The message to be displayed
     */
    log: function (msg) {
      IMAGE_LOG.html('<br />{0}'.format(msg))
    },

    /**
     * Opens the image crop and manage view, given some image data
     * @param {Number} img An image ID as stored in the database (PK)
     */
    manage: function (img) {
      var imageData = Gallery.images.get(img)
      var image = new window.Image()

      // Keep the ID, since we need it later when POSTing the crop data
      self.imageId = img

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

        // Since we just changed what image is active, we need to inform stuff that listens for image data changes
        Gallery.events.fire('gallery-imageDataChanged')
      }, 500)
    },

    /**
     * Activates a new cropping preset by the given ID. Presets are defined in the Gallery app settings
     * on the backend, and fetched through a view each time the Gallery front end module is loaded.
     * @param preset An integer representing the preset ID from the dropdown menu
     */
    preset: function (preset) {
      if (self.presets[preset] === undefined) return IMAGE_LOG.text('Ugyldig preset ID')

      // Reconfigure selection constraints
      if (self.presets[preset].aspect_ratio) {
        self.cropper.setAspectRatio(self.presets[preset].aspect_ratio_x / self.presets[preset].aspect_ratio_y)
      } else {
        // Cropper.js uses NaN to represent no aspect ratio requirements
        self.cropper.setAspectRatio(NaN)
      }

      // Update sidebar with new aspect ratio data
      var cropData = self.cropper.getData(true)
      IMAGE_HEIGHT.val(cropData.height)
      IMAGE_WIDTH.val(cropData.width)

      // Since we just switched preset, we need to inform stuff that listens for image data changes
      Gallery.events.fire('gallery-imageDataChanged')
    },

    /**
     * Resets all fields in the image cropping form
     */
    reset: function () {
      IMAGE_WIDTH.val('0')
      IMAGE_HEIGHT.val('0')
      IMAGE_NAME.val('')
      IMAGE_DESCRIPTION.val('')
      IMAGE_PHOTOGRAPHER.val('')
      IMAGE_TAGS.val('')
      // Reset preset stuff
      getCropPresetsFromServer()
    },

    /**
     * Validates the current crop selection against a preset (object with min_height, min_width etcc)
     * @param {object} preset Object with min_height, min_width etc.
     */
    validate: function (preset) {
      var _cropData = self.cropper.getData(true)
      var _errors = []

      // Perform the checks on crop data vs preset, as well as form input fields

      if (preset.min_width !== undefined && _cropData.width < preset.min_width) {
        _errors.push('Bildebredden er mindre enn minstekravet: {0}'.format(preset.min_width))
      }
      if (preset.min_height !== undefined && _cropData.height < preset.min_height) {
        _errors.push('Bildehøyden er mindre enn minstekravet: {0}'.format(preset.min_height))
      }
      if (IMAGE_NAME.val().length <= 3) {
        _errors.push('Bildet må ha et navn på mer enn 3 bokstaver.')
      }
      if (IMAGE_DESCRIPTION.val().length === 0) {
        _errors.push('Bildet må ha en beskrivelse')
      }

      // Display the errors in the status field
      if (_errors.length > 0) {
        var errorTemplate = '<br /><i>Må utbedres:</i><ul>' +
          '<% _(errors).each(function (e) { %><li><%= e %></li><% }) %></ul>'
        IMAGE_LOG.html(utils.render(errorTemplate, {errors: _errors}))
      } else {
        GalleryCrop.log('OK')
      }

      return _errors
    }
  }
})(window.jQuery, window.Cropper, new window.Utils())

var Gallery = (function ($, utils, MicroEvent, Dropzone) {
  var _events = new MicroEvent()
  var _images = {}
  var _formSelectedSingleImage = null

  // DOM references
  var BUTTON_ADD_RESPONSIVE_IMAGE = $('#add-responsive-image')
  var IMAGE_SELECTION_WRAPPER = $('#image-selection-wrapper')
  var MANAGE_BUTTON_TEXT = $('#gallery__manage-button-text')
  var THUMBNAIL_VIEW = $('#gallery__thumbnail-view')
  var DASHBOARD_MENU_GALLERY_UNHANDLED_BADGE = $('#dashboard__menu--gallery-unhandled-badge')

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
    // Declare the success callback
    var success = function (images) {
      // Update the local image cache with current data
      images = images.unhandled
      for (var i = 0; i < images.length; i++) {
        _images[images[i].id] = images[i]
      }

      // Update the manage button text and create thumbnails for the manage unhandled images view
      MANAGE_BUTTON_TEXT.text('Behandle ({0})'.format(images.length))

      // Update the sidebar menu badge as well
      var badge = '<small class="badge"><%= unhandledCount %></small>'
      if (images.length > 0) {
        DASHBOARD_MENU_GALLERY_UNHANDLED_BADGE.html(utils.render(badge, {unhandledCount: images.length}))
      } else {
        DASHBOARD_MENU_GALLERY_UNHANDLED_BADGE.html('')
      }

      createUnhandledImageThumbnails(images)
    }

    // Declare the error callback
    var error = function (xhr, errorMessage, responseText) {
      console.error('Received error: ' + xhr.responseText + ' ' + errorMessage)
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

      // Listen for form widget button events
      BUTTON_ADD_RESPONSIVE_IMAGE.on('click', function (e) {
        e.preventDefault()
        IMAGE_SELECTION_WRAPPER.slideToggle(100)
      })

      /**
       * Helper function that performs a search query to the Gallery backend. Query string is exact match and will
       * not be tokenized.
       * @param query A string containing a keyword or sentence.
       */
      var searchImages = function (query) {
        var payload = { query: query }

        Gallery.ajax('GET', '/gallery/search/', payload, function (data) {
          var html = utils.render(TMPL_IMAGE_SEARCH_RESULT, {images: data.images})
          if (!data.images.length) html = '<div class="col-md-12"><p>Ingen bilder matchet søket...</p></div></div>'
          else html += '</div>'

          $('#image-gallery-search-results').html(html)
        }, function (xhr, thrownError, statusText) {
          window.alert(thrownError)
        })
      }

      // Listen for <Enter> keypress while the search input field is :active
      $('#image-gallery-search').on('keypress', function (e) {
        if (e.keyCode === 13) {
          e.preventDefault()
          e.stopPropagation()
          searchImages($(this).val())
        }
      })

      // Listen for manual clicks to the search button
      $('#image-gallery-search-button').on('click', function (e) {
        e.preventDefault()
        searchImages($('#image-gallery-search').val())
      })

      // Place a permanent click event listener on the image widget, listening for
      // click events originating from elements classed "image-selection-thumbnail".
      // Updates the ID if the form input field and toggles highlighting.
      $('#image-gallery-search-results').on('click', '.image-selection-thumbnail', function (e) {
        if (_formSelectedSingleImage) _formSelectedSingleImage.removeClass('image-selection-thumbnail-active')
        _formSelectedSingleImage = $(this)
        _formSelectedSingleImage.addClass('image-selection-thumbnail-active')

        var inputValue = $('#responsive-image-id')
        var thumbnailWrapper = $('#single-image-field-thumbnail')

        if (inputValue.length) {
          inputValue.val(_formSelectedSingleImage.attr('data-id'))
          thumbnailWrapper.html('<img src="' + _formSelectedSingleImage.find('img').attr('src') + '" alt>')
        }
      })
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
       * Fire an event of type "event" to all registered listeners for that type.
       * @param {string} event The event type to be triggered
       * @param {*} [payload] An optional event payload
       */
      fire: function (event, payload) {
        _events.fire(event, payload)
      },

      /**
       * Register a callback function on events of the given type.
       * @param {string} event Event type
       * @param {function} callback Callback function accepting two arguments: {string} event, {*} payload
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
})(window.jQuery, new window.Utils(), window.MicroEvent, window.Dropzone)

// Initialise the Gallery module
Gallery.init()
