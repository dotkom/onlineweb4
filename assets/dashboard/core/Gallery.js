import jQuery from 'jquery';
import MicroEvent from 'common/utils/MicroEvent';
import { ajaxEnableCSRF, format, render } from 'common/utils';
import GalleryCrop from './GalleryCrop';
import GalleryUpload from './GalleryUpload';

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
<% } %>`;

const Gallery = (function PrivateGallery($) {
  const events = new MicroEvent();
  const galleryImages = {};
  let formSelectedSingleImage = null;
  let formSelectedMultipleImages = null;

  // DOM references
  const BUTTON_ADD_RESPONSIVE_IMAGE = $('#add-responsive-image');
  const BUTTON_ADD_RESPONSIVE_IMAGES = $('#add-responsive-images');
  const IMAGE_SELECTION_WRAPPER = $('#image-selection-wrapper');
  const MANAGE_BUTTON_TEXT = $('#gallery__manage-button-text');
  const THUMBNAIL_VIEW = $('#gallery__thumbnail-view');
  const DASHBOARD_MENU_GALLERY_UNHANDLED_BADGE = $('#dashboard__menu--gallery-unhandled-badge');
  const BUTTON_REMOVE_IMAGE = $('#dashboard-gallery-remove-image');
  const BUTTON_REMOVE_IMAGES = $('#dashboard-gallery-remove-images');

  /**
   * Create the HTML wrapper for the thumbnail of an UnhandledImage wrapper as a jQuery DOM object.
   * @param {object} image A JavaScript object containing id,
   * link to original image as well as link to thumbnail
   */
  const createUnhandledImageThumbnails = (images) => {
    // Clear the unhandled image thumbnail view
    THUMBNAIL_VIEW.html('');

    // Add each thumbnail and bind event listener
    for (let i = 0; i < images.length; i += 1) {
      const img = $('<img></img>');
      const imgLink = $('<a></a>').html(img);
      const imageID = images[i].id;

      img.attr({
        class: 'gallery__unhandled-image',
        'data-id': imageID,
        src: images[i].thumbnail,
      });
      imgLink.attr({
        'data-toggle': 'tab',
        href: '#gallery__edit-pane',
        role: 'tab',
      });

      THUMBNAIL_VIEW.append(imgLink);

      // Add event listener
      img.on('click', function imgClick() {
        GalleryCrop.manage($(this).attr('data-id'));
      });
    }
  };

  /**
   * Retrieve an array of all UnhandledImage objects currently in the database
   */
  const fetchUnhandledImages = () => {
    // Declare the success callback
    const success = (imagesObject) => {
      // Update the local image cache with current data
      const images = imagesObject.unhandled;
      for (let i = 0; i < images.length; i += 1) {
        galleryImages[images[i].id] = images[i];
      }

      // Update the manage button text and create thumbnails for the manage unhandled images view
      MANAGE_BUTTON_TEXT.text(format('Behandle ({0})', images.length));

      // Update the sidebar menu badge as well
      const badge = '<small class="badge"><%= unhandledCount %></small>';
      if (images.length > 0) {
        const badgeHtml = render(badge, { unhandledCount: images.length });
        DASHBOARD_MENU_GALLERY_UNHANDLED_BADGE.html(badgeHtml);
      } else {
        DASHBOARD_MENU_GALLERY_UNHANDLED_BADGE.html('');
      }

      createUnhandledImageThumbnails(images);
    };

    // Declare the error callback
    const error = (xhr, errorMessage) => {
      console.error(`Received error: ${xhr.responseText} ${errorMessage}`);
    };

    // Fetch all unhandled images from the Gallery endpoint
    Gallery.ajax('GET', '/gallery/unhandled/', null, success, error, null);
  };

  return {
    /**
     * Initialize the Gallery module.
     */
    init() {
      // Do the ajax setup
      ajaxEnableCSRF($);

      // Register retrieval of unhandled images on the newUnhandledImage event
      this.events.on('gallery-newUnhandledImage', fetchUnhandledImages);

      // Fire an initial "newUnhandledImage" event
      this.events.fire('gallery-newUnhandledImage');

      // Initialize the support modules
      GalleryCrop.init();
      GalleryUpload.init();

      // Listen for form widget button events
      BUTTON_ADD_RESPONSIVE_IMAGE.on('click', (e) => {
        e.preventDefault();
        IMAGE_SELECTION_WRAPPER.slideToggle(100);
      });

      // Listen for form widget button events
      BUTTON_ADD_RESPONSIVE_IMAGES.on('click', (e) => {
        e.preventDefault();
        IMAGE_SELECTION_WRAPPER.slideToggle(100);
      });

      // Remove set image
      BUTTON_REMOVE_IMAGE.on('click', (e) => {
        e.preventDefault();
        $('#responsive-image-id').attr('value', '');
        $('#single-image-field-thumbnail').html('Det er ikke valgt noe bilde.');
      });

      // Remove set image
      BUTTON_REMOVE_IMAGES.on('click', (e) => {
        e.preventDefault();
        //$('#responsive-image-id').attr('value', '');
        $('#single-image-field-thumbnail').html('Det er ikke valgt noe bilder.');
      });

      /**
       * Helper function that performs a search query to the Gallery backend.
       * Query string is exact match and will not be tokenized.
       * @param query A string containing a keyword or sentence.
       */
      const searchImages = (query) => {
        const payload = { query };

        Gallery.ajax('GET', '/gallery/search/', payload, (data) => {
          let html = render(TMPL_IMAGE_SEARCH_RESULT, { images: data.images });
          if (!data.images.length) html = '<div class="col-md-12"><p>Ingen bilder matchet søket...</p></div></div>';
          else html += '</div>';

          $('#image-gallery-search-results').html(html);
        }, (xhr, thrownError) => {
          window.alert(thrownError);
        });
      };

      // Listen for <Enter> keypress while the search input field is :active
      $('#image-gallery-search').on('keypress', function keypress(e) {
        if (e.keyCode === 13) {
          e.preventDefault();
          e.stopPropagation();
          searchImages($(this).val());
        }
      });

      // Listen for manual clicks to the search button
      $('#image-gallery-search-button').on('click', (e) => {
        e.preventDefault();
        searchImages($('#image-gallery-search').val());
      });

      // Place a permanent click event listener on the image widget, listening for
      // click events originating from elements classed "image-selection-thumbnail".
      // Updates the ID if the form input field and toggles highlighting.
      $('#image-gallery-search-results').on('click', '.image-selection-thumbnail', function clickThumb() {
        console.log("In search results")
        console.log($(this).parent())
        var multiple = $('#image-gallery-search-results').hasClass('multiple') 
        console.log(multiple)
        if (multiple) {
          var image = $(this);
          console.log(image)
          image.toggleClass('image-selection-thumbnail-active');

          const inputValue = $('#responsive-image-id');
          const thumbnailWrapper = $('#single-image-field-thumbnail');
        } else {
          if (formSelectedSingleImage) formSelectedSingleImage.removeClass('image-selection-thumbnail-active');
          formSelectedSingleImage = $(this);
          formSelectedSingleImage.addClass('image-selection-thumbnail-active');

          const inputValue = $('#responsive-image-id');
          const thumbnailWrapper = $('#single-image-field-thumbnail');

          if (inputValue.length) {
            inputValue.val(formSelectedSingleImage.attr('data-id'));
            thumbnailWrapper.html(`<img src="${formSelectedSingleImage.find('img').attr('src')}" alt>`);
          }
        }
      });
      /**
      $('#image-gallery-search-results.multiple').on('click', '.image-selection-thumbnail', function clickThumb() {
        //if (formSelectedMultipleImages) formSelectedMultipleImages.removeClass('image-selection-thumbnail-active');
        var image = $(this);
        console.log(image)
        image.addClass('image-selection-thumbnail-active');

        const inputValue = $('#responsive-image-id');
        const thumbnailWrapper = $('#single-image-field-thumbnail');
        /**
        if (inputValue.length) {
          inputValue.val(formSelectedMultipleImages.attr('data-id'));
          thumbnailWrapper.html(`<img src="${formSelectedMultipleImages.find('img').attr('src')}" alt>`);
        }
        
      });
      **/
    },

    /**
     * Perform an AJAX request of type "method" to "url" with the optional "data", specified
     * "success" and "error" callback functions, and optional data "type" specification.
     * @param {string} method The HTTP method
     * @param {string} url The url of the endpoint to send the request to
     * @param {object} data An optional object literal of data (can be null)
     * @param {function} success A success callback function that must accept one data argument
     * @param {function} error An error callback function that must accept
     * xhr, thrownError and responseText args
     * @param {string} type An optional data type specification
     */
    ajax(method, url, data, success, error, type) {
      const payload = {
        type: method.toUpperCase(),
        url,
        success,
        error,
      };
      if (data !== null || data !== undefined) payload.data = data;
      if (type !== null || type !== undefined) {
        if (type === 'json') {
          payload.contentType = 'application/json; charset=UTF-8';
          payload.dataType = 'json';
        }
      }
      $.ajax(payload);
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
      fire(event, payload) {
        events.fire(event, payload);
      },

      /**
       * Register a callback function on events of the given type.
       * @param {string} event Event type
       * @param {function} callback Callback function accepting
       * two arguments: {string} event, {*} payload
       */
      on(event, callback) {
        events.on(event, callback);
      },
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
      get(id) {
        return galleryImages[id];
      },
    },
  };
}(jQuery));

export default Gallery;
