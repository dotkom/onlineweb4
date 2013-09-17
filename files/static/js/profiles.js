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


//Show image name input field when chosing new image
    $('input[type=file]').change(function() {
        var filename = $('input[type=file]').val().split('\\').pop();
        $('#image-name').val(filename);
        $('#image-name').show();

        displayImage(this);
    });

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

    /* Load image when selecting file */
    function displayImage(inputBox) {
        if(inputBox.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload(function(e) {
                $('img#profile-image').attr('src', e.target.result);
            });
        }
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
});