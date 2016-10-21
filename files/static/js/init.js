var initGoogleMaps = function() {
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

    // Applying the marker to the map, but only if the map has been created
    var online_marker = new google.maps.Marker({
        map: map,
        position: new google.maps.LatLng(63.41816871425781,10.405924207023645),
        icon: '/static/img/map-marker.png',
        visible: true
    });
    return map;
}

// Fadeout alerts if they have the data-dismiss property
var timeOutAlerts = function() {
  setTimeout(function () {
    $('.alert[data-dismiss]').fadeOut()
  }, 5000)
}

$(function() {
    // ??
    $('.dropdown-toggle').dropdown();

    timeOutAlerts()

    // Init the footer-map, but don't crash if google is not found
    try {
        var map = initGoogleMaps();
    }
    catch (err){
        console.warn("Could not load Google Maps:", err);
    }

    // Reset center of the map on window-resize (using jquery-plugin to only fire the event when resizing is finished)
    $(window).on("debouncedresize",function(e) {
        if(map){
            map.panTo(new google.maps.LatLng(63.41819751959266, 10.40592152481463));
        }
    });


    /* nav bar toggle
    ---------------------------------------------------------------------------*/
    $('#mainnav-button').click(function (e) {
        if ($('.mn-nav').first().hasClass('mn-nav-open')) {
            removeAnimation()
            $('.mn-nav').removeClass('mn-nav-open')
                        .addClass('animation-in-process')
        } else {
            addAnimation()
            $('.mn-nav').addClass('mn-nav-open')
                        .addClass('animation-in-process')
        }

        setTimeout(function () {
            $('.mn-nav').removeClass('animation-in-process')
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
