import Urls from 'urls';
import $ from 'jquery';

const Filters = function Filters() {
  this.query = '';
  this.future = true;
  this.myevents = false;
};

Filters.prototype.search = function search() {
  const url = `${Urls.search_events()}?query=`;
  const query = this.query;
  let filters = '';
  filters += `&future=${this.future}`;
  filters += `&myevents=${this.myevents}`;

  const self = this;
  $.get(url + query + filters, (result) => {
    $('#events').empty();
    $('#events').append(result);
    if (!self.future) {
      // Calculate menu offset
      const offset = $('nav.subnavbar').position().top + $('nav.subnavbar').outerHeight(true);
      // Scroll to closest event
      const articles = $('#events article');
      const today = new Date();
      articles.each((i, event) => {
        const eventDate = new Date($(event).data('date'));
        if (eventDate < today) {
          // Scroll animation
          $('html, body').animate({ scrollTop: $(event).offset().top - offset }, 250);
          return false;
        }
        return true;
      });
    }
  });
};

$(() => {
  const filters = new Filters();
  filters.search();


  $('#search').keyup(function search() {
    filters.query = $(this).val();
    filters.search();
  });

  // This is a slight hack to avoid a difficult bug in jQuery
  // where some browsers tend to preserve checkbox states
  // without them being domready.
  $(document).ready(() => {
    $('#future').prop('checked', true);
  });

  $('#future').on('click', () => {
    filters.future = !filters.future;
    filters.search();
  });

  $('#myevents').on('click', () => {
    filters.myevents = !filters.myevents;
    filters.search();
  });
});
