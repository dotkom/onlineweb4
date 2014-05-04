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

function readURL(input) {

    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#large-preview').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

$("#image-input").change(function(){
    readURL(this);
});

updateUneditedFiles();
setInterval(function() {
    updateUneditedFiles();
}, 10000);

function updateUneditedFiles() {
    $.ajax({
        method: 'GET',
        url: 'number_of_untreated',
        success: function(res) {
            var res = jQuery.parseJSON(res);
            var text = "Behandle (" + res['untreated'] + ")";
            $("#edit-button > div.caption").text(text);
            console.log("updated");
        },
        crossDomain: false
    });
}
$(".bttrlazyloading").each(function() {
    console.log("faen");
    $(this).bttrlazyloading(
        {
            container: '#edit-pane'
        }
    );
});

//var bLazy = new Blazy({
//    loaded: function() {
//        console.log("FITTEEEE!");
//    },
//    success: function() {
//        console.log("HELVETE");
//    }
//});

new Blazy({
    container: '#edit-pane'
});