$(function() {
    // ??
    $('.dropdown-toggle').dropdown();
    
    // Init the footer-map
    var map = new google.maps.Map(document.getElementById("footer-map"),{
        center: new google.maps.LatLng(63.41819751959266, 10.40592152481463),
        zoom: 17,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true,
        streetViewControl: false,
        styles: [{
            featureType: "all",
            stylers: [{
                saturation: -100
            }]
        }, {
            stylers: [{
                hue: "#666666"
            }, {
                lightness: -30
            }]
        }, {
            "featureType": "poi.school",
            "stylers": [{
                "color": "#555555"
            }]
        },/* {
            "featureType": "poi.business",
            "visibility": 0,
            "stylers": [{
                "color": "#00396e"
            }, {
                "weight": 0
            }]
        },*/ {
            "featureType": "poi.park",
            "stylers": [{
                "color": "#BBBBBB"
            }]
        }, {
            "featureType": "poi.sports_complex",
            "stylers": [{
                "saturation": 4
            }, {
                "weight": 0.5
            }, {
                "color": "#bbcfbb"
            }]
        }]
    });
    
    // Applying the marker to the map
    var online_marker = new google.maps.Marker({
        map: map,
        position: new google.maps.LatLng(63.41816871425781,10.405924207023645),
        icon: '/static/img/map-marker.png',
        visible: true
    });
    
    // Reset center of the map on window-resize (using jquery-plugin to only fire the event when resizing is finished)
    $(window).on("debouncedresize",function(e) {
        console.log('fired');
        map.panTo(new google.maps.LatLng(63.41819751959266, 10.40592152481463));
    });

    /* Login / user button change on window resize
    --------------------------------------------------------------------------------- */
    var old_login_btn =  $('#login_menu a').html();
    change_login_button_view();
    
    $(window).resize(function() {
        change_login_button_view();
    });

    function change_login_button_view() {
        if ($(window).innerWidth() <= 992) {
            $('#login_menu a').html('');
            $('#login_menu a').addClass('glyphicon');
            $('#login_menu a').addClass('glyphicon-user');
        }
        else {
            $('#login_menu a').html(old_login_btn);
            $('#login_menu a').removeClass('glyphicon');
            $('#login_menu a').removeClass('glyphicon-user');
        }
    }

    $('.dropdown-menu input, .dropdown-menu button, .dropdown-menu label').click(function(e) {
        e.stopPropagation();
    });
});
