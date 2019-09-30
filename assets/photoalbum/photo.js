import $ from 'jquery';

$(document).ready(() => {
  $('.photo .big').bind('keydown', (event) => {
    if (event.keyCode === 37) { // Left
      console.log('Left arrow');// eslint-disable-line no-console
    }
    if (event.keyCode === 39) { // Right arrow
      console.log('Right arrow'); // eslint-disable-line no-console
    }
  });
});
