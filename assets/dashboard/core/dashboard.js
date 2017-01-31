import jQuery from 'jquery';
import 'common/datetimepicker';
import 'common/tablesorter';
import { ajaxEnableCSRF } from 'common/utils';

const Dashboard = (function PrivateDashboard($) {
  // Private method to bind toggling of sidebar
  const bindSidebarToggle = () => {
    $("[data-toggle='offcanvas']").click(() => {
      // If window is small enough, enable sidebar push menu
      if ($(window).width() <= 992) {
        $('.row-offcanvas').toggleClass('active');
        $('.left-side').removeClass('collapse-left');
        $('.right-side').removeClass('strech');
        $('.row-offcanvas').toggleClass('relative');
      // Else stretch
      } else {
        $('.left-side').toggleClass('collapse-left');
        $('.right-side').toggleClass('strech');
      }
    });
  };

  // Check if we should auto expand the sidebar
  const sidebarAutoExpand = () => {
    if (typeof (localStorage) !== 'undefined') {
      const sidebarValue = localStorage.getItem('ow4_dashboard_sidebar');

      if (sidebarValue !== null && sidebarValue.length > 2) {
        let expanded = false;
        $('.sidebar a').each(function sidebarExpand() {
          if (!expanded && $(this).attr('href') === sidebarValue) {
            $(this).parent().parent().show();

            // Avoid collision with identical urls (#)
            expanded = true;
          }
        });
      }
    }
  };

  // Listeners used to store what
  const bindSidebarExpand = () => {
    $('.sidebar-menu a').on('click', function sidebarExpand() {
      const url = $(this).attr('href');

      if (url.length > 2) {
        localStorage.setItem('ow4_dashboard_sidebar', url);
      } else {
        const $parent = $(this).parent();

        if ($parent.hasClass('treeview') && $parent.find('ul').is(':hidden')) {
          localStorage.setItem('ow4_dashboard_sidebar', $parent.find('ul li:first-child a').attr('href'));
        } else {
          localStorage.setItem('ow4_dashboard_sidebar', null);
        }
      }
    });
  };

  // PUBLIC methods below
  return {
    activateDateTimePickers() {
      $('.dtp').each(function dtp() {
        $(this).datetimepicker({
          locale: 'nb',
          format: 'YYYY-MM-DD HH:mm:ss',
        });
      });

      $('.dp').each(function dp() {
        $(this).datetimepicker({
          locale: 'nb',
          format: 'YYYY-MM-DD',
        });
      });

      $('.tp').each(function tp() {
        $(this).datetimepicker({
          locale: 'nb',
          format: 'HH:mm:ss',
        });
      });
    },

    // Bind expand/collapsing of sidebar elements
    init() {
      // Methods for sidebar expand
      sidebarAutoExpand();
      bindSidebarExpand();

      // Bind toggling of sidebar
      bindSidebarToggle();

      let expanded = null;

      $('.treeview-menu').each(function treeviewMenu() {
        const navMenu = $(this);
        const navItem = $(this).parent();
        navItem.on('click', 'a', () => {
          // Toggle the submenu
          navMenu.slideToggle(200);

          if (expanded !== navMenu && expanded != null) expanded.slideUp(200);

          expanded = navMenu;
        });
      });

      // Generic javascript to enable interactive tabs that do not require page reload
      const switchTab = (newActiveTab) => {
        if ($('#dashboard-tabs').length) {
          const tabElement = $('#dashboard-tabs').find(`[data-section="${newActiveTab}"]`);
          if (tabElement.length) {
            // Hide sections
            $('#tab-content section').hide();
            // Unmark currently active tab
            $('#dashboard-tabs').find('li.active').removeClass('active');
            // Update the active tab to the clicked tab and show that section
            tabElement.parent().addClass('active');
            $(`#${newActiveTab}`).show();
                        // Update URL
            window.history.pushState({}, document.title, $(tabElement).attr('href'));
          }
        }
      };

      // Hide all other tabs and show the active one when the page loads
      if ($('#dashboard-tabs').length) {
        // Hide all sections
        $('#tab-content section').hide();
        // Find the currently active tab and show it
        const activeTab = $('#dashboard-tabs').find('li.active a').data('section');
        $(`#${activeTab}`).show();

        // Set up the tabs to show/hide when clicked
        $('#dashboard-tabs').on('click', 'a', function tab(e) {
          e.preventDefault();
          const newActiveTab = $(this).data('section');
          switchTab(newActiveTab);
        });
      }

      // Fix for tabs when going 'back' in the browser history
      window.addEventListener('popstate', () => {
        // If you can figure out how to do this properly, be my guest.
      });

      // Set up AJAX CSRF for Dashboard
      ajaxEnableCSRF($);

      // Check for existence of input fields that require bootstrap datetimepicker
      // And activate it on these objects.
      this.activateDateTimePickers();

      window.addEventListener('activateDateTimePickers', () => {
        this.activateDateTimePickers();
      });

      // Activate tablesorter on all tablesorter class tables
      $('.tablesorter').tablesorter();
    },
  };
}(jQuery));

jQuery(document).ready(() => {
  Dashboard.init();
});
