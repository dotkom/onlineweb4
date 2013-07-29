$(document).ready(function() {

    function setnavs() {
        navs = {
            '#events': jQuery('#events').offset().top - 50,
            '#articles': jQuery('#articles').offset().top - 50,
            '#about': jQuery('#about').offset().top - 50,
            '#business': jQuery('#business').offset().top - 50,
            '#offline': jQuery('#offline').offset().top - 50
        };
        return navs;
    }
    function setactive() {
        $('a[href="/#events"]').addClass('active');
    }
    setactive();

    var navs = setnavs();

    function scrolltothis(from, to) {
        $("a[href='/"+from+"']").click(function(event) {
            event.preventDefault();
            var topPosition = jQuery(to).offset().top - 50; // See body margin
            jQuery('html, body').animate({scrollTop:topPosition}, 250);
        });
    }

    for (nav in navs) {
        scrolltothis(nav, nav)
    };

    function scrollspy() {
        var current = $(window).scrollTop();
        for (nav in navs) {
            var diff = current - navs[nav];
            if (diff > -20) {
                $(".top-menu-link a").removeClass('active');
                $("a[href='/"+nav+"']").addClass('active');
            }
        }
    }

    // TODO: heavy shit? Find a reliable way to setnavs instead of doing it fucking all the time.
    $(window).scroll(function() {
        navs = setnavs();
        scrollspy();
    });

});
