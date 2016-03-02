var Dashboard = (function ($) {
    
    // Private method to set up AJAX for dashboard
    var doAjaxSetup = function () {
        var csrfSafeMethod = function (method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
        }

        $.ajaxSetup({
            crossDomain: false,
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'))
                }
            }
        })
    }

    // Private method to bind toggling of sidebar
    var bind_sidebar_toggle = function () {
       $("[data-toggle='offcanvas']").click(function(e) {
            // If window is small enough, enable sidebar push menu
            if ($(window).width() <= 992) {
                $('.row-offcanvas').toggleClass('active')
                $('.left-side').removeClass("collapse-left")
                $(".right-side").removeClass("strech")
                $('.row-offcanvas').toggleClass("relative")
            // Else stretch
            } else {
                $('.left-side').toggleClass("collapse-left")
                $(".right-side").toggleClass("strech")   
            }
       })
    };

    // Check if we should auto expand the sidebar
    var sidebar_auto_expand = function () {
        if (typeof(localStorage) !== 'undefined') {
            var sidebar_value = localStorage.getItem('ow4_dashboard_sidebar');

            if (sidebar_value !== null && sidebar_value.length > 2) {
                var expanded = false;
                $('.sidebar a').each(function () {
                    if (!expanded && $(this).attr('href') == sidebar_value) {
                        $(this).parent().parent().show();

                        // Avoid collision with identical urls (#)
                        expanded = true;
                    }
                });
            }
        }
    };

    // Listeners used to store what
    var bind_sidebar_expand = function () {
        $('.sidebar-menu a').on('click', function () {
            var url = $(this).attr('href');

            if (url.length > 2) {
                localStorage.setItem('ow4_dashboard_sidebar', url);
            }
            else {
                var $parent = $(this).parent();
                
                if ($parent.hasClass('treeview') && $parent.find('ul').is(':hidden')) {
                    localStorage.setItem('ow4_dashboard_sidebar', $parent.find('ul li:first-child a').attr('href'));
                }
                else {
                    localStorage.setItem('ow4_dashboard_sidebar', null);
                }
            }
        });
    };

    // PUBLIC methods below
    return {

        // Bind expand/collapsing of sidebar elements
        init: function () {

            // Perform self-check
            if (!Dashboard.tools.performSelfCheck()) return

            // Methods for sidebar expand
            sidebar_auto_expand();
            bind_sidebar_expand();

            // Bind toggling of sidebar
            bind_sidebar_toggle();

            var expanded = null

            $('.treeview-menu').each(function () {
                var nav_menu = $(this)
                var nav_item = $(this).parent()
                nav_item.on('click', 'a', function (e) {

                    // Toggle the submenu
                    nav_menu.slideToggle(200)

                    if (expanded != nav_menu && expanded != null) expanded.slideUp(200)

                    expanded = nav_menu

                })
            })
    
            // Generic javascript to enable interactive tabs that do not require page reload
            var switchTab = function(newActiveTab) {
                if ($('#dashboard-tabs').length) {
                    tabElement = $('#dashboard-tabs').find('[data-section="'+ newActiveTab + '"]')
                    if (tabElement.length) {
                        // Hide sections
                        $('#tab-content section').hide()
                        // Unmark currently active tab
                        $('#dashboard-tabs').find('li.active').removeClass('active')
                        // Update the active tab to the clicked tab and show that section
                        tabElement.parent().addClass('active')
                        $('#' + newActiveTab).show()
                        // Update URL
                        window.history.pushState({}, document.title, $(tabElement).attr('href'))
                    }
                }
                else {
                    console.log("No element with id #dashboard-tabs found.")
                }
            }

            // Hide all other tabs and show the active one when the page loads
            if ($('#dashboard-tabs').length) {
                // Hide all sections 
                $('#tab-content section').hide()
                // Find the currently active tab and show it
                activeTab = $('#dashboard-tabs').find('li.active a').data('section')    
                $('#' + activeTab).show()

                // Set up the tabs to show/hide when clicked
                $('#dashboard-tabs').on('click', 'a', function (e) {
                    e.preventDefault()
                    newActiveTab = $(this).data('section')
                    switchTab(newActiveTab);
                })
            }

            // Fix for tabs when going 'back' in the browser history
            window.addEventListener("popstate", function(e) {
                // If you can figure out how to do this properly, be my guest.
            });

            // Set up AJAX CSRF for Dashboard
            doAjaxSetup()

            // Check for existence of input fields that require bootstrap datetimepicker
            // And activate it on these objects.
            $('.dtp').each(function (i) {
                $(this).datetimepicker({
                    locale: 'nb',
                    format: 'YYYY-MM-DD HH:mm:ss'
                })
            });
            
            $('.dp').each(function (i) {
                $(this).datetimepicker({
                    locale: 'nb',
                    format: 'YYYY-MM-DD'
                })
            });

            // Activate tablesorter on all tablesorter class tables
            $('.tablesorter').tablesorter()

            console.log('Dashboard initiated.')
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
            ajax: function (method, url, data, success, error, type) {
                var payload = {
                    type: method.toUpperCase(),
                    url: url,
                    success: success,
                    error: error
                }
                if (data !== null || data !== undefined) payload.data = data
                if (type !== null || type !== undefined) {
                    if (type === 'json') {
                        payload.contentType = 'application/json; charset=UTF-8'
                        payload.dataType = 'json'
                    }
                }
                $.ajax(payload)
            },

            // Display a status message for 5 seconds
            // 
            // :param message: String message text
            // :param tags: String of Bootstrap Alert CSS classes
            showStatusMessage: function (message, tags) {
                var id = new Date().getTime();
                var wrapper = $('.messages')
                var message = $('<div class="row" id="'+ id +'"><div class="col-md-12">' + 
                                '<div class="alert ' + tags + '">' + 
                                message + '</div></div></div>')

                if(wrapper.length == 0){
                    wrapper = $('section:first > .container:first')
                }
                message.prependTo(wrapper)

                // Fadeout and remove the alert
                setTimeout(function() {
                    $('[id=' + id +']').fadeOut();
                    setTimeout(function() {
                        $('[id=' + id +']').remove();
                    }, 5000);
                }, 5000);
            },

            // Sort a table body, given a column index
            tablesort: function (tbody, c) {

                var rows = tbody.rows
                var rlen = rows.length
                var a = new Array()
                var m, n, cells, clen

                for (m = 0; m < rlen; m++) {
                    cells = rows[m].cells
                    clen = cells.length
                    a[m] = new Array()
                    for (n = 0; n < clen; n++) {
                        a[m][n] = cells[n].innerHTML
                    }
                }

                a.sort(function (a, b) {
                    if (a[c] == b[c]) return 0
                    else return a[c] > b[c] ? 1 : -1
                })

                for (m = 0; m < rlen; m++) {
                    a[m] = "<td>" + a[m].join("</td><td>") + "</td>"
                }
                
                tbody.innerHTML = "<tr>" + a.join("</tr><tr>") + "</tr>"
            },

            // Check if we have jQuery
            performSelfCheck: function () {
                var errors = false
                if ($ == undefined) {
                    console.error('jQuery missing!')
                    errors = true
                }
                if ($.cookie == undefined) {
                    console.error('jQuery cookie plugin missing!')
                    errors = true
                }
                if (errors) return false
                else return true
            },
            
            toggleChecked: function(element) {

                var checkedIcon = 'fa-check-square-o'
                var uncheckedIcon = 'fa-square-o'
                var allITags = $(element).find('i')
                var ilen = allITags.length
                
                for (m = 0; m < ilen; m++) {
                    icon = allITags[m]
                    if ($(icon).hasClass('checked')) {
                        $(icon).removeClass('checked').removeClass(checkedIcon).addClass(uncheckedIcon)
                    }
                    else {
                        $(icon).addClass('checked').removeClass(uncheckedIcon).addClass(checkedIcon)
                    }
                }
            }
        }
    }
})(jQuery)

$(document).ready(function () {
    Dashboard.init()
})
