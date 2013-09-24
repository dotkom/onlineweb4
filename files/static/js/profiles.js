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
            url: 'profile/removeprofileimage',
            success: function() {
                $('img#profile-image').attr('src', "http://i.imgur.com/dZivKdI.gif");
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
            url: 'profile/updateactivetab',
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
                $('#image-resize').attr('src', e.target.result);
                $('#image-resize').Jcrop({
                    // start off with jcrop-light class
                    bgOpacity: 0.5,
                    bgColor: 'white',
                    addClass: 'jcrop-light',
                    boxHeight: 300,
                    aspectRatio: 3/4,
                    onChange: updateCoords,
                    onSelect: updateCoords
                },function() {
                    api = this;
                    api.setSelect([10,10,10+40,10+40]);
                    api.setOptions({ bgFade: true });
                    api.ui.selection.addClass('jcrop-selection');
                    api.allowResize = false;
                });
                api.setImage(e.target.result);

                if(formData) {
                    formData.append("image[]", file);
                }
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
    }

    var setStatus = function(statusMsg) {
        $('#status').html(statusMsg);
    }

    $('#upload-image-form').submit(function(e) {
        if (formData) {
            e.preventDefault();

            var fileInput = $('input[type=file]')[0];
            if(!fileInput || fileInput.files.length < 1) {
                setStatus("Ingen fil valgt.");
                return;
            }

            //JCrop select coordinates
            formData.append("x", x);
            formData.append("y", y);
            formData.append("x2", y);
            formData.append("y2", y);
            formData.append("w", y);
            formData.append("h", y);

            $.ajax({
                url: "profile/uploadimage",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                crossDomain: false,
                success: function (res) {
                    setStatus(res);
                }
            });
        }
        else {
            alert("standard form post");
        }
    });


    /* End image cropping and uploading*/
});

