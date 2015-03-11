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

    $('#userprofile-tabs > li > a').click(function(e) {
        e.preventDefault();
        updateActiveTab(this.getAttribute('href').substr(1));
        $(this).tab('show');
    })

    function updateActiveTab(activetab) {
        var data = JSON.stringify({active_tab : activetab});
        $.ajax({
            method: 'POST',
            data: data,
            url: 'updateactivetab/',
            crossDomain: false
        });
    }

    $('.privacybox').click(
        function() {
            var checkbox = $(this).find('input');
            var checked = checkbox.is(':checked');
            checkbox.prop('checked', !checked)

            animatePrivacyBox(this, checked);
        }
    )

    function animatePrivacyBox(checkbox, state) {
        if(state) {
            $(checkbox).stop().animate(
                {  opacity: 0.30  }, 100
            );
            $(checkbox).removeClass("on");
            $(checkbox).addClass("off");
        }
        else {
            $(checkbox).removeClass("off");
            $(checkbox).addClass("on");
            $(checkbox).stop().animate(
                {  opacity: 1.0 }, 100
            );
        }
    }

    // Popover for privacy and user image
    $('#privacy-help').popover({placement: 'bottom'});
    $('#image-help').popover({placement: 'bottom'});

/*
 JS for marks pane
*/

    function performMarkRulesClick() {
        var markscheckbox = $("#marks-checkbox");
        var checked = markscheckbox.is(':checked');
        markscheckbox.prop('checked', !checked);

        if(!checked) {
            $(".marks").removeClass("off").addClass("on");
            updateMarkRules();
        }
    }

    $(".marks").mouseup(function(e) {
	if (!($("#marks-checkbox").is(':checked'))) {
            performMarkRulesClick();
        }
    });

    $("#marks-checkbox").click(function(e){
        e.stopPropagation();
        e.preventDefault();
    });

    var updateMarkRules = function() {
        var utils = new Utils();

        $.ajax({
            method: 'POST',
            url: 'update_mark_rules/',
            data: { 'rules_accepted': true },
            success: function(res) {
                res = jQuery.parseJSON(res);
                utils.setStatusMessage(res['message'], 'alert-success');
                $(".marks").attr('disabled', true);
            },
            error: function() {
                utils.setStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
            },
            crossDomain: false
        });
    }

/*
 JS for email management.
*/

    $('button.add-new-email').click(function() {
        $('div.new-email-form').show();
        $(this).hide();
    });
    $('.emptyonclick').focus(function() {
        $(this).val('');
    });

    $('div.email-row').each(function(i, row) {
// Ajax request to delete an email
        $(row).find('button.delete').click(function() {
            email = $(row).find('p.email').text();
            deleteEmail(email, row);
        });
// Ajax request to set email as primary
        $(row).find('button.primary').click(function() { 
            email = $(row).find('p.email').text();
            setPrimaryEmail(email, row);
        });
// Ajax request to send verification mail
        $(row).find('button.verify').click(function() {
            email = $(row).find('p.email').text();
            verifyEmail(email, row);
        });
    });


    var deleteEmail = function(email, row) {
        $.ajax({
            method: 'POST',
            url: 'delete_email/',
            data: {'email':email, },
            success: function() {
                // TODO Make animation
                $(row).hide();
            },
            error: function(res) {
                var utils = new Utils();
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    utils.setStatusMessage(res['message'], 'alert-danger');
                }
                else {
                    utils.setStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
                }
            },
            crossDomain: false
        });
    }

    var setPrimaryEmail = function(email, row) {
        $.ajax({
            method: 'POST',
            url: 'set_primary/',
            data: {'email':email, },
            success: function() {
                $('button.active').removeClass('active').removeClass('btn-success').addClass('btn-default')
                    .prop('disabled', false).text('Sett primær');
                $(row).find('button.primary').addClass('active').removeClass('btn-default').addClass('btn-success')
                    .prop('disabled', true).text('Primær');
            },
            error: function(res) {
                var utils = new Utils();
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    utils.setStatusMessage(res['message'], 'alert-danger');
                }
                else {
                    utils.setStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
                }
            },
            crossDomain: false
        });
    }

    var verifyEmail = function(email, row) {
        $.ajax({
            method: 'POST',
            url: 'verify_email/',
            data: {'email':email, },
            success: function() {
                var utils = new Utils();
                utils.setStatusMessage('En ny verifikasjonsepost har blitt sendt til ' + email + '.', 'alert-success');
            },
            error: function(res) {
                var utils = new Utils();
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    utils.setStatusMessage(res['message'], 'alert-danger');
                }
                else {
                    utils.setStatusMessage('En uventet error ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
                }
            },
            crossDomain: false
        });
    }

    infomail = $('#toggle_infomail')
    infomail.on('click', function (e) {
        e.preventDefault()
        $.ajax({
            method: 'POST',
            url: 'toggle_infomail/',
            data: {},
            success: function (data) {
                res = JSON.parse(data)
                if (res['state'] === true) {
                    infomail.removeClass('btn-success')
                    infomail.addClass('btn-danger')
                    infomail.text('Deaktivér')
                }
                else {
                    infomail.removeClass('btn-danger')
                    infomail.addClass('btn-success')
                    infomail.text('Aktivér')
                }
            },
            error: function (e, s, xhr) {
                var utils = new Utils()
                utils.setStatusMessage('Det oppstod en uventet feil under endring av infomail.', 'alert-danger')
            },
            crossDomain: false
        })
    });

/*
  JS for membership  
*/

    var hasDatePicker = $(".hasDatePicker");
    if(hasDatePicker.size() > 0) {
        hasDatePicker.datepicker({
            yearRange: "2004:" + new Date().getFullYear(),
            changeYear: true,
            dateFormat: "yy-mm-dd"
        });
    }

    $(".delete-position").on('click', function(e) {
        var that = $(this);
        e.preventDefault();
        $.ajax({
            method: 'post',
            url: '/profile/deleteposition/',
            data: {'position_id' : $(this).data('position-id')},
            success: function (res) {
                var result = JSON.parse(res);
                var utils = new Utils();
                $(that).parent().remove();
                utils.setStatusMessage(result['message'], 'alert-success');
            },
            error: function (res) {
                var utils = new Utils();
                var result = JSON.parse(res);
                if(res['status'] === 500) {
                    utils.setStatusMessage(result['message'], 'alert-danger');
                }
            },
            crossDomain: false
        });
    });
});
