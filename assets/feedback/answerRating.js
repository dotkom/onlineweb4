import $ from 'jquery';
import 'jquery-bar-rating';

export default () => {
  $('.rating').barrating('show', {
    showValues: true,
    showSelectedRating: false,
  });
};
