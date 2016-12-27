import $ from 'jquery';

function Utils() {
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
  Utils.prototype.makeApiRequest = (request) => {
    $.ajax({
      url: request.url,
      type: request.type,
      data: request.data,
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      error: request.error,
      success: request.success,
    });
  };

  /* Method to add status messages which mimic django's own. */
  Utils.prototype.setStatusMessage = (message, tags) => {
    if ($('div.messages').length === 0) {
      let prnt = $('nav.subnavbar');
      if (prnt.length === 0) {
        prnt = $('nav.navbar');
      }
      $('<div class="container messages"><div class"row"><div class="message-container col-md-12"></div></div></div>').insertAfter(prnt);
    }
    const inner = $('.messages .message-container');
    const id = new Date().getTime();
    $(`<div class="alert ${tags}" id="${id}"><button type="button" class="close" data-dismiss="alert">&times;</button>${message}</div>`).appendTo(inner);

    timeOutAlerts();
  };

  /**
   * Render a template on the basis of the attributes of a data object
   * @param {object} tmpl A jQuery wrapper DOM object
   * @param {object} context An object containing the template payload
   * @return {object} Rendered DOM subtree containing provided context data
   */
  Utils.prototype.render = (tmpl, context) => {
    const node = window._.template(tmpl);
    return node(context);
  };
}

// Inject String format method if not defined
if (!String.prototype.format) {
  String.prototype.format = function () {
    const args = arguments;
    return this.replace(/{(\d+)}/g, (match, number) => typeof args[number] !== 'undefined' ? args[number] : match);
  };
}

export default Utils;
