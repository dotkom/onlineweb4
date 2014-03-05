$(document).ready(function()
{
    if($("#id_need_buddy").is(':checked'))
    {
        $("#id_buddy").prop('disabled', true);
    }
    else
    {
        $("#id_buddy").prop('disabled', false);
    }
});

$(document).ready(function()
{
    $("#id_need_buddy").click(function()
    {
        if($("#id_need_buddy").is(':checked'))
        {
            // Sets the users as sellected before disabling the element.
            $("select option").filter(function() 
            {
                return $(this).text() == username; 
            }).prop('selected', true);
            $("#id_buddy").prop('disabled', true);
        }
        else
        {
            $("#id_buddy").prop('disabled', false);
        }
    });
});

