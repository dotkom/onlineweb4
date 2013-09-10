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

/*
[
  {
    "featureType": "poi.school",
    "stylers": [
      { "color": "#555555" }
    ]
  },{
    "featureType": "poi.sports_complex",
    "stylers": [
      { "saturation": 4 },
      { "weight": 0.5 },
      { "color": "#bbcfbb" }
    ]
  },{
    "featureType": "poi.business",
    "elementType": "labels.text",
    "stylers": [
      { "visibility": "on" },
      { "color": "#3366aa" },
      { "weight": 1.6 },
      { "saturation": 100 },
      { "lightness": 11 }
    ]
  },{
    "featureType": "poi.park",
    "stylers": [
      { "color": "#bbcfbb" }
    ]
  },{
    "featureType": "poi.business",
    "stylers": [
      { "color": "#3366aa" },
      { "weight": 0.5 }
    ]
  }
]
*/

// Henter alle markere til kartet
var tempMarker0 = new google.maps.Marker({
    map: map,
    position: new google.maps.LatLng(63.41819751959266, 10.40592152481463),
    //icon: 'assets/css/gfx/kartikoner/overnatting.png',
    visible: true
});
});
