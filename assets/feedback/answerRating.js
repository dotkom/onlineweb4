import $ from 'jquery';

export default () => {
  $('.rating').barrating('show', {
    showValues: true,
    showSelectedRating: false,
  });
};
