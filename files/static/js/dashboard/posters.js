$(document).ready(function() {
    $("div.order").each(function(i, row) {
        $(row).find("button.assign").click(function() {
            assignToJob($(this).val(), row);
        });
    });
    
    var assignToJob = function(order_id, row) {
        var assign_to_id = $(row).find('form').find(':selected').val();
        var utils = Dashboard.tools
        $.ajax({
            method: 'POST',
            url: 'assign_person/',
            data: {'order_id': order_id, 'assign_to_id': assign_to_id},
            success: function() {
                $(row).css('background-color', '#b0ffb0');
                $(row).fadeOut(500);
            },
            error: function(response) {
                if (response['status'] === 412) {
                    response = JSON.parse(response['responseText']);
                    utils.setStatusMessage(response['message'], 'alert-danger');
                }
                else {
                    utils.setStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
                }
            },
            crossDomain: false
        });
    }
});
