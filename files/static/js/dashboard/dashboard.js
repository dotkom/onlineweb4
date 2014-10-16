var Dashboard = (function ($) {
    
    return {
        init: function () {
            Dashboard.bind_sidebar()
            console.log('Dashboard initiated.')
        },

        bind_sidebar: function () {

            Dashboard.bind_sidebar_toggle()

            $('.treeview-menu').each(function () {
                var nav_menu = $(this)
                var nav_item = $(this).parent()
                nav_item.on('click', 'a', function (e) {
                    // Toggle the submenu
                    nav_menu.slideToggle(200)
                })
            })
        },

        bind_sidebar_toggle: function () {
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
    }

})(jQuery)

$(document).ready(function () {
    Dashboard.init()
})
