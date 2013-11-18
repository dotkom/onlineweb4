$(function() {
    var TOP_OFFSET_ADJUST   = 65;
    var utils               = new Utils()

    var articleWidget       = new ArticleWidget(utils)
    , eventWidget           = new EventWidget(utils)
    , offlineWidget         = new OfflineWidget(utils);


    /* RENDER
    ------------------------------------------------------------------------ */
    eventWidget.render();
    offlineWidget.render();
	articleWidget.render();


    /* EVENT LISTENERS
    ------------------------------------------------------------------------ */
    // Enable tabbing in about section
    $('#about-tabs').on('click', 'a', function (e) {
        e.preventDefault();
        $(this).tab('show');
        $('html, body').animate({scrollTop: $('#about').offset().top - TOP_OFFSET_ADJUST}, 250);
    });

    // Clicking the links in the topnav
    $('.subnavbar').on('click', 'a', function (e) {
        e.preventDefault();
        jump($(this).data('section'));
    });



    /* FUNCTIONS
    ------------------------------------------------------------------------ */
    var jump = function (section) {
        if (typeof section !== 'undefined') {
            $('html, body').animate({scrollTop: $('#' + section).offset().top - TOP_OFFSET_ADJUST}, 250, function () {
                window.location.hash = '#!' + section;
            });
        }
    };
       
    // On scroll, loop the navs and swap active (if it needs to)
    var scrollspy = function () {
        var current = $(window).scrollTop();

        for (var i = 0; i < $('.subnavbar li a').length; i++) {
            var section     = '#' + $($('.subnavbar li a')[i]).data('section');
            var diff        = current - $(section).offset().top + TOP_OFFSET_ADJUST;

            if (diff > -20) {
                $(".top-menu-link.active").removeClass('active');
                $(".nav a[href='/" + section + "']").parent().addClass('active');
            }
        }
    }
    
    
   
    /* TODO: heavy shit? Find a reliable way to setnavs instead of doing it fucking all the time.
    ------------------------------------------------------------------------ */
    $(window).scroll(scrollspy);

    $(window).resize(function() {
        if ($(location).attr('hash').replace(/^#!/, '')) {
            $(window).scrollTop($($(location).attr('hash').replace(/^#!/, '')).offset().top - TOP_OFFSET_ADJUST);
        }
    });


    /* On load highlight the current menu-item if an anchor is represented
    ------------------------------------------------------------------------ */
    scrollspy();


    /* Reload fix - reposition after reload
    ------------------------------------------------------------------------ */
    if ($(location).attr('hash').replace(/^#!/, '')) {
        setTimeout(function () {
            jump($(location).attr('hash').replace(/^#!/, ''));
        }, 500);
    }
});

