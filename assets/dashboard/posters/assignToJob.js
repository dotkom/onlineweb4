import $ from 'jquery';
import { setStatusMessage } from 'common/utils/';

const assignToJob = (orderId, row) => {
  const assignToId = $(row).find('form').find(':selected').val();
  $.ajax({
    method: 'POST',
    url: 'assign_person/',
    data: { order_id: orderId, assign_to_id: assignToId },
    success() {
      $(row).css('background-color', '#b0ffb0');
      $(row).fadeOut(500);
    },
    error(response) {
      if (response.status === 400) {
        const jsonResponse = JSON.parse(response.responseText);
        setStatusMessage(jsonResponse.message, 'alert-danger');
      } else {
        setStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
      }
    },
    crossDomain: false,
  });
};

export default assignToJob;
