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
                console.log(res);
                res = JSON.parse(res);
                $('img#profile-image').attr('src', res['url']);
                $('#remove-image-modal').modal("hide");
            },
            error: function() {
                alert("Error!")
            },
            crossDomain: false
        });
    }

    $('#userprofile-tabs > li > a').click(function() {
        updateActiveTab(this.getAttribute('href').substr(1));
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
    var api;
    var formData = false;
    var x, y, x2, y2, w, h;

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
                var api;
                $('.jcrop-holder').remove();
                api = $.Jcrop('#image-resize', {
                    // start off with jcrop-light class
                    bgOpacity: 0.5,
                    bgColor: 'white',
                    addClass: 'jcrop-light',
                    boxHeight: 300,
                    aspectRatio: 3/4,
                    onChange: updateCoords,
                    onSelect: updateCoords,
                    keySupport: false,
                    allowSelect: false
                });
                api.setImage(e.target.result, function () {
                    api.setSelect([0,0,500,500]);
                });
                api.setOptions({ bgFade: true });
                api.ui.selection.addClass('jcrop-selection');
                api.allowResize = true;
                if(formData) {
                    formData.append("image", file);
                }

                $('#upload-button').show();
            }
        }
    }

    function updateCoords(c) {
        x = c.x;
        y = c.y;
        x2 = c.x2;
        y2 = c.y2;
        w = c.w;
        h = c.h;
        $('#inputx').val(c.x);
        $('#inputy').val(c.y);
        $('#inputx2').val(c.x2);
        $('#inputy2').val(c.y2);
        $('#inputw').val(c.w);
        $('#inputh').val(c.h);
    }

    var setStatus = function(statusMsg) {
        $('#status').html(statusMsg);
    }

    $('#upload-image-form').submit(function(e) {
        if (formData) {
            e.preventDefault();

            if(!imageChosen()) return;

            setStatus("Laster opp bildet...")

            //JCrop select coordinates
            formData.append("x", x);
            formData.append("y", y);
            formData.append("x2", x2);
            formData.append("y2", y2);
            formData.append("w", w);
            formData.append("h", h);

            $.ajax({
                url: "uploadimage/",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                crossDomain: false,
                success: function (res) {
                    res = JSON.parse(res);
                    setStatus(res['message']);
                    $('#profile-image').attr("src", res['image-url']);
                    $('#upload-image-modal').modal('hide');
                },
                error: function(res) {
                    setStatus(res);
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
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    alert(res['message']);
                }
                else {
                // TODO write a proper error function
                    alert("Error!");
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
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    alert(res['message']);
                }
                else {
                // TODO write a proper error function
                    alert("Error!");
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
                alert("tada");
            },
            error: function(res) {
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    alert(res['message']);
                }
                else {
                // TODO write a proper error function
                    alert("Error!");
                }
            },
            crossDomain: false
        });
    }

/*
  JS for membership  
*/

    $(".hasDatePcker").datepicker({ dateFormat: "yy-mm-dd" });
        
    $("#membership-details").submit(function(event) {
        event.preventDefault();
        $.ajax({
            method: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function() {
                alert('success');
            },
            error: function(res) {
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    alert(res['message']);
                }
                else {
                // TODO write a proper error function
                    alert("Error!");
                }
            },
            crossDomain: false
        });
    });

});


