import $ from 'jquery';

export default () => {
  $('#social-membership-application').hide();
  $('#id_field_of_study').on('change', () => {
    if ($('#id_field_of_study').val() === '40') {
      $('#social-membership-application').show();
    } else {
      $('#social-membership-application').hide();
    }
  });

  $('.manual-membership-form').hide();
  $('.manual-membership-button').on('click', () => {
    $('.manual-membership-form').show();
    $('.manual-membership-choice').hide();
  });
};
