import $ from 'jquery';
import OfflineWidget from './OfflineWidget';

const TOP_OFFSET_ADJUST = 65;

const offlineWidget = new OfflineWidget();


/* RENDER
------------------------------------------------------------------------ */
offlineWidget.render();

/* FUNCTIONS
------------------------------------------------------------------------ */
const cleanHash = () => $(location).attr('hash').replace(/^#!/, '');

const jump = (section) => {
  if (typeof section !== 'undefined') {
    $('html, body').animate({ scrollTop: $(`#${section}`).offset().top - TOP_OFFSET_ADJUST }, 250, () => {
      window.location.hash = `#!${section}`;
    });
  }
};

// On scroll, loop the navs and swap active (if it needs to)
const scrollspy = () => {
  const current = $(window).scrollTop();

  for (let i = 0; i < $('.subnavbar li a').length; i += 1) {
    const section = `#${$($('.subnavbar li a')[i]).data('section')}`;
    const diff = current - ($(section).offset().top + TOP_OFFSET_ADJUST);

    if (diff > -20) {
      $('.subnavbar li.active').removeClass('active');
      $(`a[href='/${section}']`).parent().addClass('active');
    }
  }
};

/* EVENT LISTENERS
------------------------------------------------------------------------ */
// Enable tabbing in about section
$('#about-tabs').on('click', 'a', function tabClick(e) {
  e.preventDefault();
  $(this).tab('show');

  /*
  Set anchor from tab href that matches tab pane id. Reason we need to do this is because
  we want the anchor on the format !about/foo, but that is not a valid HTML5 id.
  Instead we have about-foo, and replace the dash with a slash and prefix with a exclamation
  point to follow the front page standard.
  */
  const anchorUrl = this.href.split('#');
  if (anchorUrl.length > 1) {
    window.location.hash = `!${anchorUrl[1].replace(/-/g, '/')}`;
  }

  // Swap header
  let title = $(this).html();
  if ($(this).data('prefixom') === undefined || $(this).data('prefixom') === 'false') {
    title = `Om ${title}`;
  }

  $('#about-heading').html(title.toUpperCase());

  // Swap content
  $('html, body').animate({ scrollTop: $('#about').offset().top - TOP_OFFSET_ADJUST }, 250);
});

// Clicking the links in the topnav
$('.subnavbar').on('click', 'a', function subnavbarClick(e) {
  e.preventDefault();
  jump($(this).data('section'));
});

/* TODO: heavy shit? Find a reliable way to setnavs instead of doing it fucking all the time.
------------------------------------------------------------------------ */
$(window).scroll(scrollspy);

$(window).resize(() => {
  if (cleanHash()) {
    $(window).scrollTop($($(location).attr('hash').replace(/^#!/, '')).offset().top - TOP_OFFSET_ADJUST);
  }
});


/* On load highlight the current menu-item if an anchor is represented
------------------------------------------------------------------------ */
scrollspy();


/* Reload fix - reposition after reload
------------------------------------------------------------------------ */
if (cleanHash().length > 0) {
  const currentCleanHash = cleanHash();
  setTimeout(() => {
    if (currentCleanHash.indexOf('/') > -1) {
      const subHash = currentCleanHash.split('/');
      if (subHash.length > 1) {
        $(`a[href$="#${subHash[0]}-${subHash[1]}"]`).trigger('click');
      }
    } else {
      jump(currentCleanHash.replace(/#/, ''));
    }
  }, 500);
}

/* Menu retract on action */
$('.top-menu-link a').on('click touchend', () => {
  if ($('.navbar-toggle').is(':visible')) {
    $('.navbar-toggle').trigger('click');
  }
});
