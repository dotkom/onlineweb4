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

        // Set anchor from tab href that matches tab pane id. Reason we need to do this is because we want the anchor
        // on the format !about/foo, but that is not a valid HTML5 id. Instead we have about-foo, and replace the dash
        // with a slash and prefix with a exclamation point to follow the front page standard.
        var anchor_url = this.href.split('#');
        if (anchor_url.length > 1) {
            window.location.hash = '!' + anchor_url[1].replace(/-/g, '/');
        }

        // Swap header
        var title = $(this).html();
        if ($(this).data('prefixom') == undefined || $(this).data('prefixom') == 'false') {
            title = 'Om ' + title;
        }

        $('#about-heading').html(title.toUpperCase());

        // Swap content
        $('html, body').animate({scrollTop: $('#about').offset().top - TOP_OFFSET_ADJUST}, 250);
    });

    // Clicking the links in the topnav
    $('.subnavbar').on('click', 'a', function (e) {
        e.preventDefault();
        jump($(this).data('section'));
    });



    /* FUNCTIONS
    ------------------------------------------------------------------------ */
    var clean_hash = function () {
        return $(location).attr('hash').replace(/^#!/, '');
    };

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
                $(".subnavbar li.active").removeClass('active');
                $("a[href='/" + section + "']").parent().addClass('active');
            }
        }
    }



    /* TODO: heavy shit? Find a reliable way to setnavs instead of doing it fucking all the time.
    ------------------------------------------------------------------------ */
    $(window).scroll(scrollspy);

    $(window).resize(function() {
        if (clean_hash()) {
            $(window).scrollTop($($(location).attr('hash').replace(/^#!/, '')).offset().top - TOP_OFFSET_ADJUST);
        }
    });


    /* On load highlight the current menu-item if an anchor is represented
    ------------------------------------------------------------------------ */
    scrollspy();


    /* Reload fix - reposition after reload
    ------------------------------------------------------------------------ */
    if (clean_hash().length > 0) {
        var current_clean_hash = clean_hash();
        setTimeout(function () {
            if (current_clean_hash.indexOf('/') > -1) {
                var sub_hash = current_clean_hash.split('/');
                if (sub_hash.length > 1) {
                    $('a[href$="#' + sub_hash[0] + '-' + sub_hash[1] + '"]').trigger('click');
                }
            }
            else {
                jump(current_clean_hash);
            }
        }, 500);
    }

	/* Menu retract on action */
	$('.top-menu-link a').on('click touchend', function () {
		if ($('.navbar-toggle').is(':visible')) {
			$('.navbar-toggle').trigger('click');
		}
	});
});
