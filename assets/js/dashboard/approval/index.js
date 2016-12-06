import './less/approval.less';

$(document).ready(function() {
    $("div.application").each(function(i, row) {
        $(row).find("button.approve").click(function() {
            approveApplication($(this).val(), row);
        });
        $(row).find("button.decline").click(function() {
            that = $(this);
            // hide the first button
            $(this).prop('disabled', true);
            // show the row with message and confirmation
            confirmrow = $("#confirm" + $(this).val());
            $(confirmrow).show();
            // find the button that will actually send the decline and set some stuff on it
            $("button.sendDecline").click(function() {
                $(confirmrow).hide();
                message = $(confirmrow).find("textarea").val();
                declineApplication($(this).val(), message, row);
            });
            // cancel should hide the row and enable the first button again
            $("button.cancel").click(function() {
                $(that).prop('disabled', false);
                $(confirmrow).hide();
            });
        }).prop('disabled', false);
    });

    var approveApplication = function(application_id, row) {
        var utils = Dashboard.tools
        $.ajax({
            method: 'POST',
            url: 'approve_application/',
            data: {'application_id': application_id, },
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

    var declineApplication = function(application_id, message, row) {
        var utils = Dashboard.tools
        $.ajax({
            method: 'POST',
            url: 'decline_application/',
            data: {'application_id': application_id, 'message': message, },
            success: function() {
                $(row).css('background-color', '#f0b0b0');
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

    // Bind tablesorter on the processed approvals list
    $('#previous_approvals_list').tablesorter()
});
