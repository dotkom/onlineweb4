import { csrfSafeMethod } from 'js/common/utils';

// This small hack is needed to allow city to be fetched from bring.
// On a request to bring, crossdomain needs to be set to false
// and then restored when the request is fulfilled.
const turnOnCrossDomain = () => {
  $.ajaxSetup({
    crossDomain: true,
  });
};

const turnOffCrossDomain = () => {
  $.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
      }
    },
  });
};

const loadCity = () => {
  const zipCode = $('#zip-code').text();
  turnOnCrossDomain();
  $.ajax({
    url: `https://fraktguide.bring.no/fraktguide/api/postalCode.json?country=no&pnr=${zipCode}&callback=?`,
    dataType: 'jsonp',
    success(res) {
      $('#city').html(`&nbsp;${res.result}`);
      turnOffCrossDomain();
    },
    error() {
      turnOffCrossDomain();
    },
  });
};

export default loadCity;
