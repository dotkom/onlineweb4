import $ from 'jquery';

export default () => {
  let master_doc = $('#field-of-study-application-master-documentation');
  let social_doc = $('#field-of-study-application-documentation');

  $('#id_field_of_study').on('change', () => {
    let field_of_study = parseInt($('#id_field_of_study').val());
    social_doc.hide();
    master_doc.hide();

    if (field_of_study >= 10 && field_of_study <= 30) {
      master_doc.show();
    } else if (field_of_study === 40) {
      social_doc.show();
    }
  });
};
