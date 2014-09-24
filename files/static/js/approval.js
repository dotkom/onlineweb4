

$(document).ready(function() {
    $("div.application").each(function(i, row) {
        $(row).find("button.approve").click(function() {
            approveApplication($(this).val(), row);
        });
        $(row).find("button.decline").click(function() {
            declineApplication($(this).val(), row);
        });
    });
    
    var approveApplication = function(application_id, row) {
        var utils = new Utils();
        $.ajax({
            method: 'POST',
            url: 'approve_application/',
            data: {'application_id': application_id, },
            success: function(response) {
                response = JSON.parse(response['responseText']);
                utils.setStatusMessage(response, 'alert-success');
                // TODO Make animation
                $(row).hide();
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

    var declineApplication = function(application_id, row) {
        
    }

});
