import $ from 'jquery';
import { showStatusMessage } from 'common/utils';
import './less/approval.less';

const approveApplication = (applicationId, row) => {
  $.ajax({
    method: 'POST',
    url: 'approve_application/',
    data: { application_id: applicationId },
    success: () => {
      $(row).css('background-color', '#b0ffb0');
      $(row).fadeOut(500);
    },
    error: (response) => {
      if (response.status === 412) {
        const responseJson = JSON.parse(response.responseText);
        showStatusMessage(responseJson.message, 'alert-danger');
      } else {
        showStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
      }
    },
    crossDomain: false,
  });
};

const declineApplication = (applicationId, message, row) => {
  $.ajax({
    method: 'POST',
    url: 'decline_application/',
    data: { application_id: applicationId, message },
    success: () => {
      $(row).css('background-color', '#f0b0b0');
      $(row).fadeOut(500);
    },
    error: (response) => {
      if (response.status === 412) {
        const responseJson = JSON.parse(response.responseText);
        showStatusMessage(responseJson.message, 'alert-danger');
      } else {
        showStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
      }
    },
    crossDomain: false,
  });
};

$('div.application').each((i, row) => {
  $(row).find('button.approve').click(function approve() {
    approveApplication($(this).val(), row);
  });
  $(row).find('button.decline').click(function decline() {
    // hide the first button
    $(this).prop('disabled', true);
    // show the row with message and confirmation
    const confirmrow = $(`#confirm${$(this).val()}`);
    $(confirmrow).show();
    // find the button that will actually send the decline and set some stuff on it
    $('button.sendDecline').click(function sendDecline() {
      $(confirmrow).hide();
      const message = $(confirmrow).find('textarea').val();
      declineApplication($(this).val(), message, row);
    });
    // cancel should hide the row and enable the first button again
    $('button.cancel').click(() => {
      $(this).prop('disabled', false);
      $(confirmrow).hide();
    });
  }).prop('disabled', false);
});
