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
    $('#image-name').hide();

//Ajax request to remove profile image
    $('#confirm-delete').click(function() {
        confirmRemoveImage();
    });

    function confirmRemoveImage() {
        $.ajax({
            method: 'DELETE',
            url: 'removeprofileimage/',
            success: function(res) {
                res = JSON.parse(res);
                $('img#profile-image').attr('src', res['url']);
                $('#remove-image-modal').modal("hide");
                var utils = new Utils();
                utils.setStatusMessage(res['message'], 'alert-success');
            },
            error: function(res) {
                res = JSON.parse(res['responseText']);
                $('#remove-image-modal').modal("hide");
                var utils = new Utils();
                utils.setStatusMessage(res['message'], 'alert-danger');
            },
            crossDomain: false
        });
    }

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

    // Popover for privacy
    $('#privacy-help').popover({placement: 'bottom'});

    /* Image cropping and uploading */
    var formData = false;

    if(window.FormData) {
        formData = new FormData();
    }

    $('input[type=file]').change(function() {
        readURL(this);
    });

    function readURL(input) {

        if (input.files && input.files[0]) {
            var file = input.files[0];

            if (!file.type.match(/image.*/)) {
                return;
            }

            var reader = new FileReader();
            reader.readAsDataURL(file);

            reader.onloadend = function(e) {
                console.log(e.target.result);

                $('#profile-image-upload').prop('src', e.target.result);
                if(formData) {
                    formData.append("image", file);
                }

                $('#upload-button').show();
            }
        }
    }

    var setStatus = function(statusMsg) {
        $('#status').html(statusMsg);
    }

    $('#upload-image-form').submit(function(e) {
        if (formData) {
            e.preventDefault();
            if(!imageChosen()) return;
            setStatus("Laster opp bildet...")

            $.ajax({
                url: "uploadimage/",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                crossDomain: false,
                success: function (res) {
                    res = $.parseJSON(res);
                    $('#profile-image').attr("src", res['image-url']);
                    $('#upload-image-modal').modal('hide');

                    var utils = new Utils();
                    utils.setStatusMessage(res['message'], 'alert-success');
                },
                error: function(res) {
                    res = $.parseJSON(res['responseText']);
                    $('#upload-image-modal').modal('hide');

                    var statusMessage = "";
                    for(var i = 0; i < res['message'].length; i++) {
                        statusMessage += res['message'][i];
                        if(i != statusMessage.length-1) {
                            statusMessage += "<br>";
                        }
                    }
                    var utils = new Utils();
                    utils.setStatusMessage(statusMessage, 'alert-danger');
                }
            });
        }
        else {
            if(!imageChosen()) {
                e.preventDefault();
            }
        }
    });

    function imageChosen() {
        var fileInput = $('input[type=file]')[0];
            if(!fileInput || fileInput.files.length < 1) {
                setStatus("Ingen fil valgt.");
                return false;
            }
        return true;
    }


    /* End image cropping and uploading*/

/*
 JS for email management.
*/

    $('button.addnewemail').click(function() {
        $('tr.addnewemail').show();
        $(this).hide();
    });
    $('.emptyonclick').focus(function() {
        $(this).val('');
    });

    $('tr').each(function(i, row) {
// Ajax request to delete an email
        $(row).find('button.delete').click(function() {
            email = $(row).find('span.email').text();
            deleteEmail(email, row);
        });
// Ajax request to set email as primary
        $(row).find('button.primary').click(function() { 
            email = $(row).find('span.email').text();
            setPrimaryEmail(email, row);
        });
// Ajax request to send verification mail
        $(row).find('button.verify').click(function() {
            email = $(row).find('span.email').text();
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

/*
  JS for membership  
*/

    $(".hasDatePicker").datepicker({
        yearRange: "2004:" + new Date().getFullYear(),
        changeYear: true,
        dateFormat: "yy-mm-dd"
    });
        
    $("#membership-details").submit(function(event) {
        event.preventDefault();
        $.ajax({
            method: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function() {
                var utils = new Utils();
                utils.setStatusMessage('Detaljer for ditt medlemskap har blitt lagret.', 'alert-success');
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
    });
});


