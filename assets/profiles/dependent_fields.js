import $ from 'jquery';

export default () => {
  $('#field-of-study-application-documentation').hide();
  $('#id_field_of_study').on('change', () => {
    if ($('#id_field_of_study').val() === '40') {
      $('#field-of-study-application-documentation').show();
    } else {
      $('#field-of-study-application-documentation').hide();
    }
  });
};
