import $ from 'jquery';

export default () => {
  $('#div_id_documentation').hide();
  $('#id_field_of_study').on('change', () => {
    if ($('#id_field_of_study').val() === '40') {
      $('#div_id_documentation').show();
    } else {
      $('#div_id_documentation').hide();
    }
  });
};
