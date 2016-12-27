import $ from 'jquery';

/*
    The event module provides dynamic functions to event objects
    such as saving user selection on event extras
*/

// Global variables defined in details template
const allExtras = window.all_extras;
const selectedExtra = window.selected_extra;

const showFlashMessage = (message, tags) => {
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

  window.timeOutAlerts();
};

const ajaxRequest = (request) => {
  $.ajax({
    url: request.url,
    type: 'POST',
    data: request.data,
    headers: { 'X-CSRFToken': $.cookie('csrftoken') },
    error: request.error,
    success: request.success,
  });
};


const sendChoice = (id) => {
  const url = window.location.href.toString();
  const data = {
    extras_id: id,
    action: 'extras',
  };
  const success = (jsonData) => {
    // var line = $('#' + attendee_id > i)
    showFlashMessage(jsonData.message, 'alert-success');

    const chosenText = 'Valgt ekstra: ';
    const options = $('.extras-choice option');
    for (let i = options.length - 1; i >= 0; i -= 1) {
      if (options[i].text.indexOf(chosenText) >= 0) {
        options[i].text = allExtras[i];
        break;
      }
    }

    const selected = $('.extras-choice option:selected');
    selected.text(chosenText + selected.text());
  };
  const error = (xhr, txt, errorMessage) => {
    const message = 'Det skjedde en feil! Refresh siden og prøv igjen, eller kontakt de ansvarlige hvis det fortsatt ikke går. ';
    showFlashMessage(message + errorMessage, 'alert-danger');
  };

  // Make an AJAX request
  ajaxRequest({ method: 'POST', url, data, success, error });
};

const init = () => {
  $('.extras-choice').on('change', function changeExtraChoice() {
    const id = $(this).val();
    const text = $(this).text();
    sendChoice(id, text);
  });

  if (allExtras.length > 0 && selectedExtra === 'None') {
    const message = 'Vennligst velg et alternativ for extra bestilling. (Over avmeldingsknappen)';
    showFlashMessage(message, 'alert-warning');
  } else if (allExtras.length > 0 && selectedExtra !== '' && $.inArray(selectedExtra, allExtras) === -1) {
    const message = 'Ditt valg til ekstra bestilling er ikke lenger gyldig! Velg et nytt.';
    showFlashMessage(message, 'alert-warning');
  }
};

export default init;
