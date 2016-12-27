import jQuery from 'jquery';
import Utils from 'common/utils/Utils';
import Gallery from './Gallery';

const GalleryCrop = (function PrivateGalleryCrop($, Cropper, utils) {
  // DOM References
  const CROP_IMAGE = $('#gallery__image-edit--submit');
  const EDIT_CONTAINER = $('#gallery__image-edit-container');
  const IMAGE_LOG = $('#gallery__image-edit--log');
  const IMAGE_PRESET = $('#gallery__image-edit--preset');
  const IMAGE_HEIGHT = $('#gallery__image-edit--height');
  const IMAGE_WIDTH = $('#gallery__image-edit--width');
  const IMAGE_ZOOM_IN = $('#gallery__image-edit__zoom-in');
  const IMAGE_ZOOM_OUT = $('#gallery__image-edit__zoom-out');
  const IMAGE_SET_CROP_MODE = $('#gallery__image-edit__crop');
  const IMAGE_SET_DRAG_MODE = $('#gallery__image-edit__drag');
  const IMAGE_RESET = $('#gallery__image-edit__reset');
  const IMAGE_DESCRIPTION = $('#gallery__image-edit--description');
  const IMAGE_NAME = $('#gallery__image-edit--name');
  const IMAGE_PHOTOGRAPHER = $('#gallery__image-edit--photographer');
  const IMAGE_TAGS = $('#gallery__image-edit--tags');
  const MANAGE_BUTTON = $('#gallery__edit-button');
  const MANAGE_PANE = $('#gallery__manage-pane');
  const MODAL_CROPFAILED = $('#gallery__image-edit__crop-failed');
  const MODAL_PROCESSING = $('#gallery__image-edit__processing');
  const MODAL_SUCCESS = $('#gallery__image-edit__crop-success');
  const RESET_BUTTON = $('#gallery__image-edit__back');
  const PREVIEW_IMAGE = $('#gallery__image-edit--preview');

  // Cropper
  let cropper = null;
  let imageId = -1;
  const presets = {};
  const options = {
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
    cropmove() {
      const cropData = cropper.getData(true);

      $('#gallery__image-edit--width').val(cropData.width);
      $('#gallery__image-edit--height').val(cropData.height);

      // Since we just moved the crop window, we need to inform stuff
      // that listens for image data changes
      Gallery.events.fire('gallery-imageDataChanged');
    },
  };

  /**
   * Binds all necessary event listeners for the GalleryCrop module
   */
  const bindEventListeners = () => {
    // Zoom in
    IMAGE_ZOOM_IN.on('click', () => {
      cropper.zoom(0.1);
      Gallery.events.fire('gallery-imageDataChanged');
    });

    // Zoom out
    IMAGE_ZOOM_OUT.on('click', () => {
      cropper.zoom(-0.1);
      Gallery.events.fire('gallery-imageDataChanged');
    });

    // Activates crop selection tool
    IMAGE_SET_CROP_MODE.on('click', () => {
      cropper.setDragMode('crop');
    });

    // Activates mouse move tool
    IMAGE_SET_DRAG_MODE.on('click', () => {
      cropper.setDragMode('move');
    });

    // Reset the selection
    IMAGE_RESET.on('click', () => {
      cropper.clear();
    });

    // Listen for changes directly to the height field
    IMAGE_HEIGHT.on('keyup', () => {
      const imageData = cropper.getData(true);
      imageData.height = Number(IMAGE_HEIGHT.val());
      cropper.setData(imageData);
      Gallery.events.fire('gallery-imageDataChanged');
    });

    // Listen for changes directly to the width field
    IMAGE_WIDTH.on('keyup', () => {
      const imageData = cropper.getData(true);
      imageData.width = Number(IMAGE_WIDTH.val());
      cropper.setData(imageData);
      Gallery.events.fire('gallery-imageDataChanged');
    });

    IMAGE_NAME.on('keyup', () => {
      Gallery.events.fire('gallery-imageDataChanged');
    });

    IMAGE_DESCRIPTION.on('keyup', () => {
      Gallery.events.fire('gallery-imageDataChanged');
    });

    // Listen for crop button click event
    CROP_IMAGE.on('click', (e) => {
      e.preventDefault();
      GalleryCrop.crop(presets[IMAGE_PRESET.children('option:selected').val()]);
    });

    // Listen for changes to image data, so we can perform necessary tasks
    // like sanity checks / validation
    Gallery.events.on('gallery-imageDataChanged', () => {
      GalleryCrop.validate(presets[IMAGE_PRESET.children('option:selected').val()]);
    });

    // Hop back to the unhandled image thumbnail preview on crop success
    Gallery.events.on('gallery-imageCropSuccessful', (e, data) => {
      MODAL_PROCESSING.modal('hide');
      RESET_BUTTON.click();
      GalleryCrop.reset();

      const tmpl = '<p>Bilde {0} ({1}) av type "{2}" ble beskåret uten problemer</p>'.format(
        data.name, data.id, data.preset,
      );
      MODAL_SUCCESS.find('.modal-body').html(tmpl);
      MODAL_SUCCESS.modal('show');

      // Fire the newUnhandledImage event, as it will force a reload of the server side state
      Gallery.events.fire('gallery-newUnhandledImage');
    });

    // Handle crop failure events
    Gallery.events.on('gallery-imageCropFailed', () => {
      MODAL_PROCESSING.modal('hide');
      MODAL_CROPFAILED.modal('show');
    });
  };

  /**
   * Retrieves the list of available presets from the server via an AJAX request.
   */
  const getCropPresetsFromServer = () => {
    IMAGE_LOG.text('Henter preset fra tjeneren...');

    // Declare success callback
    const success = (data) => {
      // Update the select dropdown
      IMAGE_PRESET.html('');
      const optionTemplate = '<option value="<%= val %>" <%= selected %>><%= description %></option>';
      for (let i = 0; i < data.presets.length; i += 1) {
        const name = data.presets[i].name;
        presets[name] = data.presets[i];
        const context = {
          val: name,
          description: data.presets[i].description,
        };
        if (i === 0) context.selected = 'selected';
        else context.selected = '';

        IMAGE_PRESET.append(utils.render(optionTemplate, context));
      }

      // Listen for changes to selected preset
      IMAGE_PRESET.on('change', function changePreset() {
        const preset = $(this).children('option:selected').val();
        GalleryCrop.preset(preset);
      });
    };

    // Declare error callback
    const error = (xhr, errorMessage, responseText) => {
      IMAGE_LOG.text('En feil har oppstått');
      console.error(responseText);
    };

    Gallery.ajax('GET', '/gallery/preset/', null, success, error, null);
  };

  return {
    /**
     * Initialize the GalleryCrop module
     */
    init() {
      // Check if we are rendering the manage-pane directly
      if (MANAGE_PANE.length && window.location.href.indexOf('#gallery__manage-pane') !== -1) {
        MANAGE_BUTTON.click();
      }

      // If we see the image crop preset selection dropdown, we are in edit mode
      // and can safely bind the crop event listeners.
      if (IMAGE_PRESET.length > 0) {
        bindEventListeners();
        // Presets are defined in the Gallery app settings file
        getCropPresetsFromServer();
      }
    },

    /**
     * Performs a validation check before sending a POST request
     * to the backend with the current cropData.
     *
     * @param {object} preset A preset object containing attributes
     * such as min_width, aspect_ratio etc.
     */
    crop(preset) {
      const errors = GalleryCrop.validate(preset);

      // Fire cropFailed and return prematurely if errors exist
      if (errors.length > 0) return Gallery.events.fire('gallery-imageCropFailed');

      // Prepare the image crop data payload with necessary fields
      const payload = cropper.getData(true);
      payload.id = Number(imageId);
      payload.name = IMAGE_NAME.val();
      payload.description = IMAGE_DESCRIPTION.val();
      payload.photographer = IMAGE_PHOTOGRAPHER.val() || '';
      payload.preset = IMAGE_PRESET.children(':selected').val();
      payload.tags = IMAGE_TAGS.val() || '';

      // Declare the success callback
      const success = (callbackData) => {
        const data = callbackData;
        data.name = payload.name;
        data.preset = payload.preset;
        Gallery.events.fire('gallery-imageCropSuccessful', data);
      };
      // Declare the error callback
      const error = (xhr, errorMessage) => {
        Gallery.events.fire('gallery-imageCropFailed');
        console.error(`Received error: ${xhr.responseText} ${errorMessage}`);
      };

      // Lock user out from GUI
      MODAL_PROCESSING.modal('show');

      Gallery.ajax('POST', '/gallery/crop/', payload, success, error);
      return null;
    },

    /**
     * Prints a log message to the log field in the right hand sidebar of the edit image view
     * @param {string} msg The message to be displayed
     */
    log(msg) {
      IMAGE_LOG.html('<br />{0}'.format(msg));
    },

    /**
     * Opens the image crop and manage view, given some image data
     * @param {Number} img An image ID as stored in the database (PK)
     */
    manage(img) {
      const imageData = Gallery.images.get(img);
      const image = new window.Image();

      // Keep the ID, since we need it later when POSTing the crop data
      imageId = img;

      image.id = 'gallery__image-active';
      image.src = imageData.image;

      EDIT_CONTAINER.html(image);
      PREVIEW_IMAGE.attr({ src: imageData.image });

      // For reasons still unknown, cropper needs a timeout before being able to wrap the img.
      // Hooking the wrapper to the img load event does not work.
      setTimeout(() => {
        if (cropper !== null && cropper !== undefined) cropper.destroy();
        cropper = new window.Cropper(image, options);

        const cropData = cropper.getData();
        IMAGE_HEIGHT.val(cropData.height);
        IMAGE_WIDTH.val(cropData.width);

        // Since we just changed what image is active, we need to inform
        // stuff that listens for image data changes
        Gallery.events.fire('gallery-imageDataChanged');
      }, 500);
    },

    /**
     * Activates a new cropping preset by the given ID.
     * Presets are defined in the Gallery app settings on the backend,
     * and fetched through a view each time the Gallery front end module is loaded.
     * @param preset An integer representing the preset ID from the dropdown menu
     */
    preset(presetID) {
      const preset = presets[presetID];
      if (preset === undefined) return IMAGE_LOG.text('Ugyldig preset ID');

      // Reconfigure selection constraints
      if (preset.aspect_ratio) {
        cropper.setAspectRatio(preset.aspect_ratio_x / preset.aspect_ratio_y);
      } else {
        // Cropper.js uses NaN to represent no aspect ratio requirements
        cropper.setAspectRatio(NaN);
      }

      // Update sidebar with new aspect ratio data
      const cropData = cropper.getData(true);
      IMAGE_HEIGHT.val(cropData.height);
      IMAGE_WIDTH.val(cropData.width);

      // Since we just switched preset, we need to inform stuff that listens for image data changes
      Gallery.events.fire('gallery-imageDataChanged');
      return null;
    },

    /**
     * Resets all fields in the image cropping form
     */
    reset() {
      IMAGE_WIDTH.val('0');
      IMAGE_HEIGHT.val('0');
      IMAGE_NAME.val('');
      IMAGE_DESCRIPTION.val('');
      IMAGE_PHOTOGRAPHER.val('');
      IMAGE_TAGS.val('');
      // Reset preset stuff
      getCropPresetsFromServer();
    },

    /**
     * Validates the current crop selection against a preset
     * (object with min_height, min_width etc)
     *
     * @param {object} preset Object with min_height, min_width etc.
     */
    validate(preset) {
      const cropData = cropper.getData(true);
      const errors = [];

      // Perform the checks on crop data vs preset, as well as form input fields

      if (preset.min_width !== undefined && cropData.width < preset.min_width) {
        errors.push('Bildebredden er mindre enn minstekravet: {0}'.format(preset.min_width));
      }
      if (preset.min_height !== undefined && cropData.height < preset.min_height) {
        errors.push('Bildehøyden er mindre enn minstekravet: {0}'.format(preset.min_height));
      }
      if (IMAGE_NAME.val().length <= 3) {
        errors.push('Bildet må ha et navn på mer enn 3 bokstaver.');
      }
      if (IMAGE_DESCRIPTION.val().length === 0) {
        errors.push('Bildet må ha en beskrivelse');
      }

      // Display the errors in the status field
      if (errors.length > 0) {
        const errorTemplate = '<br /><i>Må utbedres:</i><ul>' +
          '<% _(errors).each(function (e) { %><li><%= e %></li><% }) %></ul>';
        IMAGE_LOG.html(utils.render(errorTemplate, { errors }));
      } else {
        GalleryCrop.log('OK');
      }

      return errors;
    },
  };
}(jQuery, window.Cropper, new Utils()));

export default GalleryCrop;
