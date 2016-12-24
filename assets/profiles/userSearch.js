import $ from 'jquery';
import Hogan from 'hogan.js';
import Urls from 'urls';

const userSearchTemplate = [
  '<img width="100%" src="{{ image }}" alt="" />',
  '<span data-id="{{ id }}" class="user-meta"><h4>{{ name }}</h4>',
].join('');

$('#search-users').typeahead({
  remote: `${Urls.profiles_api_user_search()}?query=%QUERY`,
  updater(item) {
    return item;
  },
  template: userSearchTemplate,
  valueKey: 'id',
  engine: Hogan,
}).on('typeahead:selected typeahead:autocompleted', (e, datum) => {
  window.location = `/profile/view/${datum.username}`;
});

// Spin until everything is ready
$('.affix-spinner').spin();

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
