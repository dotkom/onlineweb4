import $ from 'jquery';
import { ajaxEnableCSRF } from 'common/utils';

export default () => {
  $('.vote-button').click(function voteButtonClick() {
    ajaxEnableCSRF($);
    const button = $(this);
    const userid = button.data('user-id');
    $.ajax({
      type: 'post',
      url: '/genfors/admin/user/can_vote',
      data: { 'user-id': userid },
      success(data) {
        if (data.success) {
          button.removeClass('btn-danger btn-success');
          if (data.can_vote) {
            button.addClass('btn-success');
            button.text('Ja');
          } else {
            button.addClass('btn-danger');
            button.text('Nei');
          }
        } else {
          const modal = $('#errorModal');
          modal.find('.modal-body > p').text(data.error);
          modal.modal();
        }
      },
      dataType: 'json',
    });
  });
};
