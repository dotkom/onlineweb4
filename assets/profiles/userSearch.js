import $ from 'jquery';
import { userTypeahead } from 'common/typeahead';
import Spinner from 'spin.js';
import './less/typeahead.less';


export default () => {
  userTypeahead($('#search-users'), (e, datum) => {
    window.location = `/profile/view/${datum.username}`;
  });

  // Spin until everything is ready
  const affixSpinner = document.querySelector('.affix-spinner');
  new Spinner().spin(affixSpinner);

  // Jump to right place when section in affix is clicked
  $('#affix a').on('click', function affixClick(event) {
    const offset = 80;
    event.preventDefault();
    window.location.hash = $(this).attr('href');
    scrollBy(0, -offset);
  });


  // When all images are loaded, disable spinner, show affix and enable scrollspy
  $(window).load(() => {
    $('.affix-spinner-wrapper').remove();
    $('.affix').show();
    $('body').scrollspy({
      target: '#affix',
      offset: 90,
    });
  });
};
