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

    var TOP_OFFSET_ADJUST = 65;

    // Render on load
    eventWidget.render(update_pos);
    offlineWidget.render();
	articleWidget.render(update_pos);

    // Enable tabbing in about section
    $('#about-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show',update_pos);
        $('html, body').animate({scrollTop: $('#about').offset().top - TOP_OFFSET_ADJUST}, 250);
    });


    /* FUNCTIONS
    ------------------------------------------------------------------------ */
    var jump = function (section) {
        if (typeof section !== 'undefined') {
            
            $('html, body').animate({scrollTop: $('#'+section).offset().top - TOP_OFFSET_ADJUST}, 250, function () {
                window.location.hash = '#!' + section;
            });
        }
    };
       
    // On scroll, loop the navs and swap active (if it needs to)
    function scrollspy() {
        var current = $(window).scrollTop();
        var last = null;
        for (nav in navs) {
            var diff = current - $(nav).offset().top + TOP_OFFSET_ADJUST;
            if (diff > -20) {
                $(".top-menu-link.active").removeClass('active');
                $(".nav a[href='/"+nav+"']").parent().addClass('active');
                last = nav;
            }
        }
    }
    
    // Update position of the sections
    function update_pos () {
        $('body > section').each(function () {
            // Checking if the current section is a part of the scroll-thingy
            var idn = '#'+this.id;
            if (idn in navs) {
                navs[idn] = $(this).offset().top - TOP_OFFSET_ADJUST;
            }
        });
    }
    
    // Clicking the links in the topnav
    $('.subnavbar').on('click', 'a', function(e) {
        e.preventDefault();
        jump($(this).data('section'));
    });
   


    /* TODO: heavy shit? Find a reliable way to setnavs instead of doing it fucking all the time.
    ------------------------------------------------------------------------ */
    $(window).scroll(scrollspy);

    $(window).resize(function() {
        if ($(location).attr('hash').replace(/^#!/, '')) {
            $(window).scrollTop($($(location).attr('hash').replace(/^#!/, '')).offset().top - TOP_OFFSET_ADJUST);
        }
    });

    // On load highlight the current menu-item if an anchor is represented
    scrollspy();


    /* Reload fix - reposition after reload
    ------------------------------------------------------------------------ */
    if ($(location).attr('hash').replace(/^#!/, '')) {
        setTimeout(function () {
            jump($(location).attr('hash').replace(/^#!/, '').substring(1));
        }, 500);
    }
});

