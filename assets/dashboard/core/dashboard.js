import jQuery from 'jquery';
import { csrfSafeMethod } from 'common/utils';

const Dashboard = (function PrivateDashboard($) {
    // Private method to set up AJAX for dashboard
  const doAjaxSetup = () => {
    $.ajaxSetup({
      crossDomain: false,
      beforeSend(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
        }
      },
    });
  };

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
      // Perform self-check
      if (!Dashboard.tools.performSelfCheck()) return;

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
      doAjaxSetup();

            // Check for existence of input fields that require bootstrap datetimepicker
            // And activate it on these objects.
      this.activateDateTimePickers();

            // Activate tablesorter on all tablesorter class tables
      $('.tablesorter').tablesorter();
    },

    tools: {
            // Perform an AJAX request
            //
            // :param method: Can be POST, GET etc.
            // :param url: URL of the endpoint
            // :param data: Either null or an object of data fields
            // :param success: success function callback
            // :param error: error function callback
            // :param type: Either null (default is application/x-www-form-urlencoded)
            //              or 'json'
      ajax(method, url, data, success, error, type) {
        const payload = {
          type: method.toUpperCase(),
          url,
          success,
          error,
        };
        if (data !== null || data !== undefined) payload.data = data;
        if (type !== null || type !== undefined) {
          if (type === 'json') {
            payload.contentType = 'application/json; charset=UTF-8';
            payload.dataType = 'json';
          }
        }
        $.ajax(payload);
      },

            // Display a status message for 5 seconds
            //
            // :param message: String message text
            // :param tags: String of Bootstrap Alert CSS classes
      showStatusMessage(message, tags) {
        const id = new Date().getTime();
        let wrapper = $('.messages');
        const messageElement = $(`<div class="row" id="${id}"><div class="col-md-12">` +
                                `<div class="alert ${tags}">${
                                message}</div></div></div>`);

        if (wrapper.length === 0) {
          wrapper = $('section:first > .container:first');
        }
        messageElement.prependTo(wrapper);

                // Fadeout and remove the alert
        setTimeout(() => {
          $(`[id=${id}]`).fadeOut();
          setTimeout(() => {
            $(`[id=${id}]`).remove();
          }, 5000);
        }, 5000);
      },

      // Sort a table body, given a column index
      tablesort(tbody, c) {
        const rows = tbody.rows;
        const rlen = rows.length;

        const a = [];
        let cells;
        let clen;
        for (let m = 0; m < rlen; m += 1) {
          cells = rows[m].cells;
          clen = cells.length;
          a[m] = [];
          for (let n = 0; n < clen; n += 1) {
            a[m][n] = cells[n].innerHTML;
          }
        }

        a.sort((a1, a2) => {
          if (a1[c] === a2[c]) {
            return 0;
          }
          return a1[c] > a2[c] ? 1 : -1;
        });

        for (let m = 0; m < rlen; m += 1) {
          a[m] = `<td>${a[m].join('</td><td>')}</td>`;
        }


        // eslint-disable-next-line no-param-reassign
        tbody.innerHTML = `<tr>${a.join('</tr><tr>')}</tr>`;
      },

            // Check if we have jQuery
      performSelfCheck() {
        let errors = false;
        if ($ === undefined) {
          errors = true;
        }
        if ($.cookie === undefined) {
          errors = true;
        }
        return !errors;
      },

      toggleChecked(element) {
        const checkedIcon = 'fa-check-square-o';
        const uncheckedIcon = 'fa-square-o';
        const allITags = $(element).find('i');
        const ilen = allITags.length;

        let icon;
        for (let m = 0; m < ilen; m += 1) {
          icon = allITags[m];
          if ($(icon).hasClass('checked')) {
            $(icon).removeClass('checked').removeClass(checkedIcon).addClass(uncheckedIcon);
          } else {
            $(icon).addClass('checked').removeClass(uncheckedIcon).addClass(checkedIcon);
          }
        }
      },
    },
  };
}(jQuery));

jQuery(document).ready(() => {
  Dashboard.init();
});

// TODO: Rewrite code to use modules instead of using a global variable
window.Dashboard = Dashboard;
