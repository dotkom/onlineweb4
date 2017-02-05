import jQuery from 'jquery';
import Dropzone from 'dropzone';
import 'dropzone/dist/dropzone.css';
import './less/dropzone.less';
import Gallery from './Gallery';

const GalleryUpload = (function PrivateGalleryUpload($) {
  // DOM references
  const UPLOAD_PANE = $('#gallery__upload-pane');

  return {
    /**
     * Initialize the GalleryUpload module
     */
    init() {
      // Fetch unhandled images on dropzone upload queue complete
      if (UPLOAD_PANE.length) {
        /*
        Sadly, since the Dropzone instance event bind (.on()) did not work, and dynamic generation
        of Dropzones without the class="dropzone" attribute fails to append the dropzone class,
        we must use the autoDiscover aproach, but disable the autodiscover, so we get the styling,
        while being able to hook into onqueuecomplete event.
        */
        Dropzone.autoDiscover = false;

        // Transform the upload form to a dropzone instance
        return new Dropzone('#gallery__image-upload-form', {
          action: '/gallery/upload',
          clickable: true,
          init() {
            this.on('queuecomplete', () => {
              Gallery.events.fire('gallery-newUnhandledImage');
            });
          },
        });
      }
      return null;
    },
  };
}(jQuery));

export default GalleryUpload;
