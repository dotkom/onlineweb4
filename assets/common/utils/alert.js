import $ from 'jquery';

// Fadeout alerts if they have the data-dismiss property
export const timeOutAlerts = () => {
  setTimeout(() => {
    $('.alert[data-dismiss]').fadeOut();
  }, 5000);
};

// TODO: Remove duplicate methods that more or less do the same thing

/* Method to add status messages which mimic django's own. */
export const setStatusMessage = (message, tags) => {
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

export const showFlashMessage = (message, tags) => {
  const id = new Date().getTime();
  let wrapper = $('.messages');
  const messageElement = $(`
    <div class="row" id="${id}">
      <div class="col-md-12">
        <div class="alert ${tags}">${message}</div>
      </div>
    </div>
  `);

  if (wrapper.length === 0) {
    wrapper = $('section:first > .container:first');
  }
  messageElement.prependTo(wrapper);

  timeOutAlerts();
};

// Display a status message for 5 seconds
//
// :param message: String message text
// :param tags: String of Bootstrap Alert CSS classes
export const showStatusMessage = (message, tags) => {
  const id = new Date().getTime();
  let wrapper = $('.messages');
  const messageElement = $(`<div class="row" id="${id}"><div class="col-md-12">` +
                          `<div class="alert ${tags}">${
                          message}</div></div></div>`);

  if (wrapper.length === 0) {
    wrapper = $('section:first > .container:first');
  }
  messageElement.prependTo(wrapper);

  // Fadeout and remove the alert
  setTimeout(() => {
    $(`[id=${id}]`).fadeOut();
    setTimeout(() => {
      $(`[id=${id}]`).remove();
    }, 5000);
  }, 5000);
};
