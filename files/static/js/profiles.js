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
    // Generic javascript to enable interactive tabs that do not require page reload
    var switchTab = function(newActiveTab) {
        if ($('#profile-tabs').length) {
            tabElement = $('#profile-tabs').find('[data-section="'+ newActiveTab + '"]')
            if (tabElement.length) {
                // Hide sections
                $('#tab-content section').hide()
                // Unmark currently active tab
                $('#profile-tabs').find('li.active').removeClass('active')
                // Update the active tab to the clicked tab and show that section
                tabElement.parent().addClass('active')
                $('#' + newActiveTab).show()
                // Update URL
                window.history.pushState({}, document.title, $(tabElement).attr('href'))
            }
        }
        else {
            console.log("No element with id #profile-tabs found.")
        }
    }

    // Hide all other tabs and show the active one when the page loads
    if ($('#profile-tabs').length) {
        // Hide all sections 
        $('#tab-content section').hide()
        // Find the currently active tab and show it
        activeTab = $('#profile-tabs').find('li.active a').data('section')    
        $('#' + activeTab).show()

        // Set up the tabs to show/hide when clicked
        $('#profile-tabs').on('click', 'a', function (e) {
            e.preventDefault()
            newActiveTab = $(this).data('section')
            switchTab(newActiveTab);
        })
    }

    // Fix for tabs when going 'back' in the browser history
    window.addEventListener("popstate", function(e) {
        // If you can figure out how to do this properly, be my guest.
    });

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
            $(checkbox).removeClass("on");
            $(checkbox).addClass("off");
        }
        else {
            $(checkbox).removeClass("off");
            $(checkbox).addClass("on");
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
                utils.setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
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
                    utils.setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
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
                    utils.setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
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
                    utils.setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
                }
            },
            crossDomain: false
        });
    }

    var toggleSubscription = function(list) {
        listID = $('#toggle_' + list)
        $.ajax({
            method: 'POST',
            url: 'toggle_' + list + '/',
            data: {},
            success: function (data) {
                res = JSON.parse(data)
                if (res['state'] === true) {
                    listID.removeClass('btn-success')
                    listID.addClass('btn-danger')
                    listID.text('Deaktivér')
                }
                else {
                    listID.removeClass('btn-danger')
                    listID.addClass('btn-success')
                    listID.text('Aktivér')
                }
            },
            error: function (e, s, xhr) {
                var utils = new Utils()
                utils.setStatusMessage('Det oppstod en uventet feil under endring.', 'alert-danger')
            },
            crossDomain: false
        })
    }

    infomail = $('#toggle_infomail')
    infomail.on('click', function (e) {
        e.preventDefault()
        toggleSubscription('infomail')        
    });

    jobmail = $('#toggle_jobmail')
    jobmail.on('click', function (e) {
        e.preventDefault()
        toggleSubscription('jobmail')        
    });

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
