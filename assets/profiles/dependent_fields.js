import $ from 'jquery';

export default () => {
  let master_doc = $('#field-of-study-application-master-documentation');
  let social_doc = $('#field-of-study-application-documentation');
  social_doc.hide();
  master_doc.hide();

  $('#id_field_of_study').on('change', () => {
      let field_of_study = parseInt($('#id_field_of_study').val());

    if (field_of_study >= 10 && field_of_study <= 30){
      social_doc.hide();
      master_doc.show();
    } else if (field_of_study === 40){
      social_doc.show();
      master_doc.hide();
    } else{
      social_doc.hide();
      master_doc.hide();
    }
  });
};
