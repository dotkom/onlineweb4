import { debouncedResize } from 'common/utils';

const google = window.google;

export const createGoogleMaps = () => {
  const map = new google.maps.Map(document.getElementById('footer-map'), {
    center: new google.maps.LatLng(63.415510, 10.404668),
    zoom: 15,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    disableDefaultUI: true,
    streetViewControl: false,
    styles: [
      {
        featureType: 'all',
        stylers: [
          { saturation: -100 },
        ],
      },
      {
        stylers: [
          { hue: '#666666' },
          { lightness: -30 },
        ],
      },
      {
        featureType: 'poi.school',
        stylers: [
          { color: '#b3b3b3' },
        ],
      },
      {
        featureType: 'poi.park',
        stylers: [
          { color: '#d2e4c4' },
        ],

      },
      {
        featureType: 'road.local',
        elementType: 'all',
        stylers: [
          { hue: '#f4f4f4' },
          { lightness: 52 },
        ],
      },
      {
        featureType: 'poi.sports_complex',
        stylers: [
          { saturation: 4 },
          { weight: 0.5 },
          { color: '#bad5aa' },
        ],
      },
    ],
  });

  // Applying the marker to the map, but only if the map has been created
  // eslint-disable-next-line no-new
  new google.maps.Marker({
    map,
    position: new google.maps.LatLng(63.415510, 10.404668),
    icon: '/static/img/map-marker.png',
    visible: true,
  });
  return map;
};

export const initGoogleMaps = () => {
  // Init the footer-map, but don't crash if google is not found
  let map;
  try {
    map = createGoogleMaps();
  } catch (err) {
    console.warn('Could not load Google Maps:', err); // eslint-disable-line no-console
  }

  // Reset center of the map on window-resize
  debouncedResize(() => {
    if (map) {
      map.panTo(new google.maps.LatLng(63.415510, 10.404668));
    }
  });
};
