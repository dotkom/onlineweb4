$(function() {
    // Defining all the navs on the frontpage
    var navs = {
        '#events': $('#events').offset().top,
        '#articles': $('#articles').offset().top,
        '#offline': $('#offline').offset().top,
        '#business': $('#business').offset().top,
        '#about': $('#about').offset().top
    };
    
    var utils = new Utils();
    var eventWidget = new EventWidget(utils);
    var offlineWidget = new OfflineWidget(utils);
    var articleWidget = new ArticleWidget(utils);

    // Render on load
    eventWidget.render(update_pos);
    offlineWidget.render(156, 10, update_pos);
	articleWidget.render(update_pos);

    // Render on resize
    $(window).on('debouncedresize',function() {
        offlineWidget.render(156, 10, update_pos);
    });

    // Enable tabbing in about section
    $('#about-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show',update_pos);
        // Above callback is broken. Does not scroll to anchor.
        $('html, body').animate({scrollTop: $('#about').offset().top - 75}, 250);
    });
       
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
    
    // Update position of the sections
    function update_pos () {
        $('body > section').each(function () {
            // Checking if the current section is a part of the scroll-thingy
            var idn = '#'+this.id;
            if (idn in navs) {
                navs[idn] = $(this).offset().top - 55;
            }
        });
    }
    
    // Clicking the links in the topnav
    $('.nav a').on('click',function(e) {
        //e.preventDefault();
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

