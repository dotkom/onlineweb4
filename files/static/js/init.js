$(function() {
    // ??
    $('.dropdown-toggle').dropdown();

    // Fadeout alerts
    setTimeout(function () {
        $('.alert').fadeOut();
    }, 5000);

    // Init the footer-map
    var map = new google.maps.Map(document.getElementById("footer-map"),{
        center: new google.maps.LatLng(63.41819751959266, 10.40592152481463),
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP,

        disableDefaultUI: true,
        streetViewControl: false,

        styles: [
            {
                "featureType": "all",
                "stylers": [
                    {
                        "saturation": -100
                    }
                ]
            },
            {
                "stylers": [
                    { "hue": "#666666" },
                    { "lightness": -30 }
                ]
            },
            {
                "featureType": "poi.school",
                "stylers": [
                    { "color": "#b3b3b3" }
                ]
            },
            {
                "featureType": "poi.park",
                "stylers": [
                    { "color": "#d2e4c4" }
                ]

            },
            {
                "featureType": "road.local",
                "elementType": 'all',
                "stylers": [
                    { "hue": '#f4f4f4' },
                    { "lightness": 52 }
                ]
            },
            {
                "featureType": "poi.sports_complex",
                "stylers": [
                    { "saturation": 4 },
                    { "weight": 0.5 },
                    { "color": "#bad5aa" }
                ]
            }
        ]
    });

    // Applying the marker to the map
    var online_marker = new google.maps.Marker({
        map: map,
        position: new google.maps.LatLng(63.41816871425781,10.405924207023645),
        icon: '/static/img/map-marker.png',
        visible: true
    });

    // Reset center of the map on window-resize (using jquery-plugin to only fire the event when resizing is finished)
    // Also swap event image sources for proper resolution on mobile view
    $(window).on("debouncedresize",function(e) {
        map.panTo(new google.maps.LatLng(63.41819751959266, 10.40592152481463));

        var mobile = false;

        if ($(window).innerWidth() < 768) {
            mobile = true;
        }

        $('#eventimage img').each(function (index) {
            var event_image_source;
            image_path = $(this).attr('src').split('_');
            image_ext = image_path[image_path.length - 1].split('.')[1];
            if (mobile) {
                image_path[image_path.length - 1] = "main." + image_ext;
            }
            else {
                image_path[image_path.length - 1] = "thumb." + image_ext;
            }
            event_image_source = image_path.join("_");
            $(this).attr('src', event_image_source);
        });
    });


    /* nav bar toggle
    ---------------------------------------------------------------------------*/
    $('#mainnav-button').click(function (e) {
        if ($('.mn-nav').first().hasClass('open')) {
            removeAnimation()
            $('.mn-nav').removeClass('open')
                        .removeClass('animation-complete')
        } else {
            addAnimation()
            $('.mn-nav').addClass('open')
                        .removeClass('animation-complete')
        }
        
        setTimeout(function () {
            $('.mn-nav').addClass('animation-complete')
        }, 300)
    })

    function addAnimation() {
        var svg = document.querySelectorAll('.mn-svg')

        svg[0].setAttribute('class', 'mn-svg rotate-button')
        svg[1].setAttribute('class', 'mn-svg rotate-button-ccw')
        document.querySelector('rect.mn-svg-rect-top').setAttribute('class', 'mn-svg-rect-top transform-button')
        document.querySelector('.mn-svg-rect-bottom').setAttribute('class', 'mn-svg-rect-bottom transform-button')
    }

    function removeAnimation() {
        var svg = document.querySelectorAll('.mn-svg')

        svg[0].setAttribute('class', 'mn-svg')
        svg[1].setAttribute('class', 'mn-svg')
        document.querySelector('rect.mn-svg-rect-top').setAttribute('class', 'mn-svg-rect-top')
        document.querySelector('.mn-svg-rect-bottom').setAttribute('class', 'mn-svg-rect-bottom')
    }


    /* Menu element change
    --------------------------------------------------------------------------------- */
    var paths = window.location.pathname.split('/');
    var activeTab = paths[1];
    // Making sure that events don't highlight the archive menu
    if(activeTab !== 'events' || paths.length === 3) {
        $(".mn-nav a[href='/"+activeTab+"/']").parent().addClass('active');
    }

    switch (window.location.pathname) {
        case "/article/archive":
        case "/offline/":
            $(".mn-nav a[href='/events/']").parent().addClass('active');
    }


    /* Login / user button change on window resize
    --------------------------------------------------------------------------------- */
    $('.dropdown-menu input, .dropdown-menu button, .dropdown-menu label').click(function(e) {
        e.stopPropagation();
    });

    // Removes 300 ms delay on touch via libs/fastclick.js
    FastClick.attach(document.body);

});
