import $ from 'jquery';
import Cookies from 'js-cookie';

/**
 * Checks whether an HTTP method is considered CSRF safe or not
 * @param {string} method An HTTP method as string
 * @returns {boolean} true if the provided HTTP method is CSRF-safe. False otherwise.
 */
export const csrfSafeMethod = method => (
  (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method.toUpperCase()))
);

export const ajaxEnableCSRF = (jQuery) => {
  jQuery.ajaxSetup({
    beforeSend(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
      }
    },
  });
};

/* Static method to make single API requests */
export const makeApiRequest = (request) => {
  $.ajax({
    url: request.url,
    type: request.type,
    data: request.data,
    headers: { 'X-CSRFToken': Cookies.get('csrftoken') },
    error: request.error,
    success: request.success,
  });
};

export const cityFromZipCode = zipCode => (
  new Promise((resolve, reject) => {
    fetch(`https://fraktguide.bring.no/fraktguide/api/postalCode.json?country=no&pnr=${zipCode}`, { mode: 'cors' })
    // To JSON
    .then(response => response.json())
    // JSON looks like { result: 'city', ...}
    .then(json => json.result)
    // Resolve promise with city name
    .then(resolve)
    // Otherwise reject
    .catch(reject);
  })
);

// Perform an AJAX request
//
// :param method: Can be POST, GET etc.
// :param url: URL of the endpoint
// :param data: Either null or an object of data fields
// :param success: success function callback
// :param error: error function callback
// :param type: Either null (default is application/x-www-form-urlencoded)
//              or 'json'
export const ajax = (method, url, data, success, error, type) => {
  const payload = {
    type: method.toUpperCase(),
    url,
    success,
    error,
  };
  if (data !== null || data !== undefined) payload.data = data;
  if (type !== null || type !== undefined) {
    if (type === 'json') {
      payload.contentType = 'application/json; charset=UTF-8';
      payload.dataType = 'json';
    }
  }
  $.ajax(payload);
};
