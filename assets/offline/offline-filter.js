import $ from 'jquery';
import { debouncedResize } from 'common/utils';

/*
    Written by: Thomas Gautvedt with the help of God, Jesus and the rest of my friends at the zoo
    License: to kill
    Owner: Online
    Descrition: Welcome to epic hardcore javascript
      that ended up 10 times more complicated than it should…
    Encouragement: ENJOY!
*/

// Variables for the people
const buzy = false; // Please wait….!"/&"&/"&/"
let offlineNumInRow = 1; // Number of issues in a single row (may change on resize)
// Number of total rows (calculated based on the number of total issues to display)
let offlineTotalRows = 1;
let numIssuesToDisplay = 8; // Number of total issues
const numIssuesToDisplayMax = numIssuesToDisplay; // Don't ask...
let offlineNumInRowPrevious = 1337; // The previous number of total issues


// Appending arrows and numbers to the navigation
function initPageinator() {
  // Show/hide
  if (offlineTotalRows === 1) {
    if ($('#offline-nav').is(':visible')) {
      $('#offline-nav').hide();
    }
  } else if ($('#offline-nav').is(':hidden')) {
    $('#offline-nav').show();
  }


  // Removing first
  $('#offline-nav ul.pagination').empty();

  // Last/prev
  $('#offline-nav ul.pagination').append(`
    <li class="disabled">
      <a id="offline-nav-first" href="#">&#171;</a>
    </li>
    <li class="disabled paddright">
      <a id="offline-nav-prev" href="#">&#8249;</a>
    </li>
  `);

  // Nums
  for (let i = 0; i < offlineTotalRows; i += 1) {
    $('#offline-nav ul.pagination').append(`
      <li${(i === 0) ? ' class="active first"' : ''}>
        <a class="offline-nav" id="page-${i}" href="#">
          ${i + 1}
        </a>
      </li>
    `);
  }

  // Next/last
  $('#offline-nav ul.pagination').append(`
    <li class="paddleft${(offlineTotalRows === 1) ? ' disabled' : ''}">
      <a id="offline-nav-next" href="#">&#8250;</a>
    </li>
    <li${(offlineTotalRows === 1) ? ' class="disabled"' : ''}>
      <a id="offline-nav-last" href="#">&#187;</a>
    </li>
  `);

  // Clicky!
  $('#offline-nav .active a').trigger('click');
}

// Retarded function that mostly set variables we're using later on
// …aaand resizing the viewport of the container
function initOffline(state) {
  // Deciding how many issues we are actually dealing with
  if ($('.offline_issue.displayable').length > numIssuesToDisplay) {
    if ($('.offline_issue.displayable').length > numIssuesToDisplayMax) {
      numIssuesToDisplay = numIssuesToDisplayMax;
    } else {
      numIssuesToDisplay = $('.offline_issue.displayable').length;
    }
  } else {
    numIssuesToDisplay = $('.offline_issue.displayable').length;
  }

  // Number of issues in one row (this can change based on the width of the page)
  offlineNumInRow = parseInt(Math.floor($('#offline-wrapper').width() / 182), 10);

  // Getting how many rows we have to display at once to display the minimum number of issues
  const offlineRowsMinimum = parseInt(Math.ceil(numIssuesToDisplay / offlineNumInRow), 10);

  // Animating the height of the container
  $('#offline-wrapper').stop().animate({ height: (offlineRowsMinimum * 230) }, 400);

  // Storing total number of rows with issues
  offlineTotalRows = parseInt(Math.ceil($('.offline_issue.displayable').length / (offlineNumInRow * offlineRowsMinimum)), 10);

  // Checking if we need to trigger a click and repaint the menu
  if (offlineNumInRowPrevious === 1337) { // <- I know...
    offlineNumInRowPrevious = offlineTotalRows;
  // I know, retarded solution
  } else if (offlineNumInRowPrevious !== offlineTotalRows || state) {
    offlineNumInRowPrevious = offlineTotalRows;

    // Redraw the nav
    initPageinator();
  } else {
    offlineNumInRowPrevious = offlineTotalRows;
  }
}

// Function for filtering issues
function filter(year) {
  // Looping all issues
  $('.offline_issue').each(function offlineIssue() {
    const $obj = $(this);

    // Adding/removing displayable on the issues depending on the filter's year
    if (parseInt(year, 10) === parseInt($obj.data('year'), 10)) {
      if (!$obj.hasClass('displayable')) { $obj.addClass('displayable'); }
    } else if ($obj.hasClass('displayable')) {
      $obj.removeClass('displayable');
    }
  });

  // Aaaaand then we fix variables and fix the viewport/nav
  initOffline(true);
}

// jQuery goes here!
$(() => {
  // Clicking years to filter issues
  $('.filter-year').on('click', function yearClick(e) {
    if (e.preventDefault) {
      e.preventDefault();
    } else {
      e.stop();
    }

    // Showing the reset-shiiiiit
    if ($('#filter-reset').is(':hidden')) {
      $('#filter-reset').fadeIn(400);
    }

    // Check if currently animating
    if (!buzy) {
      // Swap classes
      $('#nav-header .active').removeClass('active');
      $(this).parent().addClass('active');

      // The sort
      filter($(this).html());
    }
  });

  // Clearing the filter
  $('#filter-reset').on('click', (e) => {
    if (e.preventDefault) {
      e.preventDefault();
    } else {
      e.stop();
    }

    // Hide the reset-shit
    $('#filter-reset').fadeOut(400);

    // Checking if currently animated and filter is set
    if (!buzy && $('#nav-header .active').length !== 0) {
      // Resetting issues to display
      numIssuesToDisplay = numIssuesToDisplayMax;

      // Removing active menu-point
      $('#nav-header .active').removeClass('active');

      // Adding displayable to all issues
      $('.offline_issue').each(function offlineIssue() {
        const $obj = $(this);
        if (!$obj.hasClass('displayable')) {
          $obj.addClass('displayable');
        }
      });

      // …and finally initing the display-function
      initOffline(true);
    }
  });

    // Click on the nav-buttons (arrows and numbers
  $('#offline-nav').on('click', 'a', function offlineNavClick(e) {
    if (e.preventDefault) {
      e.preventDefault();
    } else {
      e.stop();
    }

    // Can I has zhe object
    const $obj = $(this);

    // Doing stuff if nonmongo-user
    if (!$obj.parent().hasClass('disabled')) {
      // Pre-selected index
      const selectedIndex = parseInt($('#offline-nav ul li.active a').attr('id').split('-')[1], 10);
      let clickedIndex;
      // Getting selectedIndex
      if ($obj.hasClass('offline-nav')) {
        clickedIndex = $obj.attr('id').split('-')[1];
        // The current nav-button is an indexed one
      } else if (this.id === 'offline-nav-prev' || this.id === 'offline-nav-next') {
        // The current nav-button is previous/next
        if (this.id === 'offline-nav-prev') {
          clickedIndex = selectedIndex - 1;
        } else {
          clickedIndex = selectedIndex + 1;
        }
      } else if (this.id === 'offline-nav-first') {
        // Håkej, so the current nav-button is first/last
        clickedIndex = 0;
      } else {
        clickedIndex = $('.offline-nav').length - 1;
      }

      // Hide all the visible issues and fade in the new ones
      let num = 0;
      if ($('.offline_issue:visible').length > 0) {
        // We can run an animation here
        $('.offline_issue:visible').fadeOut(400, () => {
          if ($('.offline_issue:animated').length === 0) {
            // Done fading out
            $('.offline_issue.displayable').each(function offlineIssueDisplayable() {
              // Checking to see if this is one of the issues that we can display on the first page,
              // or if this goes on the 2nd, 3rd … one
              const startIndex = numIssuesToDisplay * parseInt(clickedIndex, 10);
              const endIndex = startIndex + numIssuesToDisplay;
              if (num >= (startIndex) && num < (endIndex)) {
                $(this).stop().fadeIn(400);
              }

              // Incr
              num += 1;
            });
          }
        });
      } else {
        // There are no visible issues (is this even possible…?),
        // so just fade 'em. Comments in section ^
        $('.offline_issue.displayable').each(function offlineIssueDisplayable() {
          const startIndex = numIssuesToDisplay * parseInt(clickedIndex, 10);
          const endIndex = startIndex + numIssuesToDisplay;
          if (num >= (startIndex) && num < (endIndex)) {
            $(this).fadeIn(400);
          }

          num += 1;
        });
      }

      // Removing active
      $('#offline-nav .active').removeClass('active');

      // Setting new active
      $('.offline-nav').eq(clickedIndex).parent().addClass('active');

      // Getting the current selected page-id
      const newSelectedIndex = $('#offline-nav ul li.active a').attr('id').split('-')[1];

      // Just checking if we have more than one page...
      if ($('.offline-nav').length > 1) {
        if (newSelectedIndex === 0) {
          // First page! Set the left buttons disabled
          $('#offline-nav-first').parent().addClass('disabled');
          $('#offline-nav-prev').parent().addClass('disabled');

          if ($('#offline-nav-next').parent().hasClass('disabled')) {
            $('#offline-nav-next').parent().removeClass('disabled');
            $('#offline-nav-last').parent().removeClass('disabled');
          }
        } else if (newSelectedIndex === ($('.offline-nav').length - 1)) {
          // Last page! Set the frikking right buttons disabled
          $('#offline-nav-next').parent().addClass('disabled');
          $('#offline-nav-last').parent().addClass('disabled');

          if ($('#offline-nav-prev').parent().hasClass('disabled')) {
            $('#offline-nav-prev').parent().removeClass('disabled');
            $('#offline-nav-first').parent().removeClass('disabled');
          }
        }
      }
    }
  });

  // Resize container 'n shit
  initOffline(false);

  // Fikser paginator
  initPageinator();

  // On resize to avoid 32948239842834 events firering at the same time)
  debouncedResize(initOffline(false));
});
