import $ from 'jquery';

export const csrfSafeMethod = method => (
  // these HTTP methods do not require CSRF protection
  /^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
);

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
