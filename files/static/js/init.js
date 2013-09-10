$(function() {
    $('.dropdown-toggle').dropdown();
    
    var map = new google.maps.Map(document.getElementById("footer-map"),{
    center: new google.maps.LatLng(63.41819751959266, 10.40592152481463),
    zoom: 17,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
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

// Henter alle markere til kartet
var tempMarker0 = new google.maps.Marker({
    map: map,
    position: new google.maps.LatLng(63.41816871425781,10.405924207023645),
    icon: '/static/img/map-marker.png',
    visible: true
});
});
