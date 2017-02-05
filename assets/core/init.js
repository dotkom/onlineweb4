import $ from 'jquery';

const addAnimation = () => {
  const svg = document.querySelectorAll('.mn-svg');

  svg[0].setAttribute('class', 'mn-svg rotate-button');
  svg[1].setAttribute('class', 'mn-svg rotate-button-ccw');
  document.querySelector('rect.mn-svg-rect-top').setAttribute('class', 'mn-svg-rect-top transform-button');
  document.querySelector('.mn-svg-rect-bottom').setAttribute('class', 'mn-svg-rect-bottom transform-button');
};

const removeAnimation = () => {
  const svg = document.querySelectorAll('.mn-svg');

  svg[0].setAttribute('class', 'mn-svg');
  svg[1].setAttribute('class', 'mn-svg');
  document.querySelector('rect.mn-svg-rect-top').setAttribute('class', 'mn-svg-rect-top');
  document.querySelector('.mn-svg-rect-bottom').setAttribute('class', 'mn-svg-rect-bottom');
};


export default () => {
  /* nav bar toggle
  ---------------------------------------------------------------------------*/
  $('#mainnav-button').click(() => {
    if ($('.mn-nav').first().hasClass('mn-nav-open')) {
      removeAnimation();
      $('.mn-nav').removeClass('mn-nav-open').addClass('animation-in-process');
    } else {
      addAnimation();
      $('.mn-nav').addClass('mn-nav-open').addClass('animation-in-process');
    }

    setTimeout(() => {
      $('.mn-nav').removeClass('animation-in-process');
    }, 300);
  });

  /* Menu element change
  --------------------------------------------------------------------------------- */
  const paths = window.location.pathname.split('/');
  const activeTab = paths[1];
  // Making sure that events don't highlight the archive menu
  if (activeTab !== 'events' || paths.length === 3) {
    $(`.mn-nav a[href='/${activeTab}/']`).parent().addClass('active');
  }

  const pathname = window.location.pathname;
  if (pathname === '/article/archive' || pathname === '/offline/') {
    $(".mn-nav a[href='/events/']").parent().addClass('active');
  }

  /* Login / user button change on window resize
  --------------------------------------------------------------------------------- */
  $('.dropdown-menu input, .dropdown-menu button, .dropdown-menu label').click((e) => {
    e.stopPropagation();
  });
};
