/* AJAX SETUP FOR CSRF */
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
    }
});
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
/* END AJAX SETUP */

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
        var utils = new Utils();
        $.ajax({
            method: 'POST',
            url: 'approve_application/',
            data: {'application_id': application_id, },
            success: function() {
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

    var declineApplication = function(application_id, message, row) {
        var utils = new Utils();
        $.ajax({
            method: 'POST',
            url: 'decline_application/',
            data: {'application_id': application_id, 'message': message, },
            success: function() {
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

});
