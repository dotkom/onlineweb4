var Filters = function () {

  this.query = '';
  this.future = true;
  this.myevents = false;
};

Filters.prototype.search = function () {
    var url = Urls.search_events() + '?query=';
    var query = this.query;
    var filters = '';
    filters   += '&future=' + this.future;
    filters     += '&myevents=' + this.myevents;

    var self = this;
    $.get(url + query + filters, function (result) {
      $('#events').empty();
      $('#events').append(result);
      if(!self.future) {
        // Calculate menu offset
        var offset = $('nav.subnavbar').position().top+$('nav.subnavbar').outerHeight(true);
        // Scroll to closest event
        var articles = $('#events article');
        var today = new Date();
        articles.each(function(i, event) {
          var event_date = new Date($(event).data('date'));
          if(event_date < today) {
            // Scroll animation
            $('html, body').animate({scrollTop: $(event).offset().top - offset}, 250);
            return false;
          }
        });
      }
    });
  };

$(function () {

  var filters = new Filters();
  filters.search();


  $('#search').keyup(function () {
    filters.query = $(this).val();
    filters.search();
  });

  // This is a slight hack to avoid a difficult bug in jQuery where some browsers tend to preserve checkbox states
  // without them being domready.
  $(document).ready(function () {
    $('#future').prop('checked', true);
  });

  $('#future').on('click', function () {
    filters.future = !filters.future;
    filters.search();
  });

  $('#myevents').on('click', function () {
    filters.myevents = !filters.myevents;
    filters.search();
  });
});
