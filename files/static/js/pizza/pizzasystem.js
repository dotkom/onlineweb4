$(document).ready(function() {
    if($("#id_need_buddy").is(':checked')) {
        $("#id_buddy").parent().parent().hide();
    }
    else {
        $("#id_buddy").parent().parent().show();
    }
    
    $("#id_need_buddy").click(function() {
        if($("#id_need_buddy").is(':checked')) {
            // Sets the users as sellected before disabling the element.
            $("select option").filter(function()  {
                return $(this).text() == username; 
            }).prop('selected', true);
            $("#id_buddy").parent().parent().slideUp();
        }
        else {
            $("#id_buddy").parent().parent().slideDown();
        }
    });
});

