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
    }

    // PUBLIC methods below
    return {

        // Bind expand/collapsing of sidebar elements
        init: function () {

            // Perform self-check
            if (!Dashboard.tools.performSelfCheck()) return

            // Bind toggling of sidebar
            bind_sidebar_toggle()

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

            // Set up AJAX CSRF for Dashboard
            doAjaxSetup()

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
                var wrapper = $('.messages')
                var message = $('<div class="row"><div class="col-md-12">' + 
                                '<div class="alert ' + tags + '">' + 
                                message + '</div></div></div>')

                wrapper.html(message)
                setTimeout(function () {
                    message.fadeOut(200)
                }, 5000)
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
            }
        }
    }
})(jQuery)

$(document).ready(function () {
    Dashboard.init()
})
