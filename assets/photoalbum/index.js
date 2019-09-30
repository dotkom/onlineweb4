import $ from 'jquery';

import './less/photoalbum.less';

$(document).ready(() => {
  $('.photo_edit').click((event) => {
    const photo = $(event.target);
    photo.toggleClass('image-selection-thumbnail-active');
    const parent = photo.parent();

    parent.toggleClass('image-selection-thumbnail-active');
  });

  $('#show_report_photo_form').click(() => {
    // button.style["visibility"] = "hidden"
    $('#show_report_photo_form').toggleClass('hidden');
    $('#report_photo_form').toggleClass('hidden');
  });

  $('.photo .big').bind('keydown', (event) => {
    if (event.keyCode === 37) { // Left
      console.log('Left arrow'); // eslint-disable-line no-console
    }
    if (event.keyCode === 39) { // Right arrow
      console.log('Right arrow'); // eslint-disable-line no-console
    }
  });
});

