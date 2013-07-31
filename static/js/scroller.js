$(document).ready(function() {
    // Defining all the navs on the frontpage
    var navs = {
        '#events': $('#events').offset().top,
        '#articles': $('#articles').offset().top,
        '#about': $('#about').offset().top,
        '#business': $('#business').offset().top,
        '#offline': $('#offline').offset().top
    };
        
    // On scroll, loop the navs and swap active (if it needs to)
    function scrollspy() {
        var current = $(window).scrollTop();
        for (nav in navs) {
            var diff = current - navs[nav];
            if (diff > -20) {
                $(".top-menu-link a.active").removeClass('active');
                $(".nav a[href='/"+nav+"']").addClass('active');
            }
        }
    }
    
    // Clicking the links in the topnav
    $('.nav a').on('click',function(e) {
        e.preventDefault();
        var $that = $(this);
        var jumpto_section = $that.data('section');
        if (typeof jumpto_section !== 'undefined') {
            var top_position = navs['#'+jumpto_section];
            $('html, body').animate({scrollTop: top_position}, 250);
        }
    });
    
    // TODO: heavy shit? Find a reliable way to setnavs instead of doing it fucking all the time.
    $(window).scroll(scrollspy);
    
    // On load highlight the current menu-item if an anchor is represented
    scrollspy();
});
