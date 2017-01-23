import $ from 'jquery';
import Webshop from './Webshop';
import WebshopGallery from './WebshopGallery';

Webshop.init();

// Gallery image chooser
if ($('#webshop-image-list').size() > 0) {
  WebshopGallery.init();
}
