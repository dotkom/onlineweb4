import $ from 'jquery';

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
    beforeSend: (xhr, settings) => {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
      }
    },
  });
};


export const ajaxRequest = (request) => {
  $.ajax({
    url: request.url,
    type: 'POST',
    data: request.data,
    headers: { 'X-CSRFToken': $.cookie('csrftoken') },
    error: request.error,
    success: request.success,
  });
};

/* adapted from djangoproject.com */
/* Static method */
function getCookie(name) {
  if (document.cookie) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = $.trim(cookies[i]);
      if (cookie.substring(0, name.length + 1) === `${name}=`) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
  }
  return null;
}

/* Static method to make single API requests */
export const makeApiRequest = (request) => {
  $.ajax({
    url: request.url,
    type: request.type,
    data: request.data,
    headers: { 'X-CSRFToken': getCookie('csrftoken') },
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
