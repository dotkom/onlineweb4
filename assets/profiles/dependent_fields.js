import $ from 'jquery';

export function DependentDocumentation() {
    $('#div_id_documentation').hide();
    $('#id_field_of_study').on("change", function(){
        if ($('#id_field_of_study').val() === "40"){
            $('#div_id_documentation').show();
        } else {
            $('#div_id_documentation').hide();
        }
    })
}
