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
                "color": "#b3b3b3"
            }]
       /* }, {
            "featureType": "poi.business",
            "visibility": 0,
            "stylers": [{
                "color": "#00396e"
            }, {
                "weight": 0
           }] */
        }, {
            "featureType": "poi.park",
            "stylers": [{
                "color": "#d2e4c4"
            }]
            
},{  
    "featureType": "road.local",  
    elementType: 'all',  
    "stylers": [  
        { hue: '#f4f4f4' },  
        
        { lightness: 52 }
    ]  

          
        }, {
            "featureType": "poi.sports_complex",
            "stylers": [{
                "saturation": 4
            }, {
                "weight": 0.5
            }, {
                "color": "#bad5aa"
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
        map.panTo(new google.maps.LatLng(63.41819751959266, 10.40592152481463));
    });




    /* Menu element change
    --------------------------------------------------------------------------------- */
    $(".nav.navbar-nav a[href='"+window.location.pathname+"']").parent().addClass('active');

    switch (window.location.pathname) {
        case "/article/archive":
        case "/offline/":
            $(".navbar .nav.navbar-nav a[href='/events/']").parent().addClass('active');
    }


    /* Login / user button change on window resize
    --------------------------------------------------------------------------------- */
    var old_login_btn       =  $('#login_menu a').html();
    var active_link_clone   = $('.navbar .nav.navbar-nav .active').clone(true);

    change_subnavbar_behaviour();

    $(window).resize(function() {
        change_subnavbar_behaviour();
    });

    function change_subnavbar_behaviour() {
        var active_link = $('.navbar .nav.navbar-nav .active');

        if ($('.subnavbar').length) {
            if ($(window).innerWidth() < 768) {
                if (!active_link.hasClass('appended')) {
                    active_link.append($('.subnavbar div').html());
                    active_link.addClass('appended');
                }
            }
            else {
                active_link.html(active_link_clone.html());
                active_link.removeClass('appended');
            }
        }
    }

    $('.dropdown-menu input, .dropdown-menu button, .dropdown-menu label').click(function(e) {
        e.stopPropagation();
    });

});
