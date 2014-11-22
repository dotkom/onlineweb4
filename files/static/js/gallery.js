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

$("#zoominbutton").click(function() {
    var image = $('#editing-image');
    image.cropper('zoom', 0.1);
});

$("#zoomoutbutton").click(function() {
    var image = $('#editing-image');
    image.cropper('zoom', -0.1);
});

$("#resetbutton").click(function() {
    var image = $('#editing-image');
    image.cropper('reset', true);
});

$("#originalimagebutton").click(function() {
    var image = $("#editing-image");
    window.open(image.attr("src"));
});


setInterval(function() {
    updateUneditedFiles();
}, 500000);


var updateUneditedFiles = function() {
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

updateUneditedFiles();

$(".bttrlazyloading").each(function() {
    $(this).bttrlazyloading(
        {
            container: '#edit-pane'
        }
    );
});


var fetchUnhandledImages = function() {

    setUpdateSpin();

    $.ajax({
        method: 'GET',
        url: 'get_all_untreated',
        success: function(res) {
            var res = jQuery.parseJSON(res);
            updateAllUnhandledImages(res['untreated']);
            setUpdateRefresh();
        },
        error: function() {
            setUpdateRefresh();
        },
        crossDomain: false
    });
};


var setUpdateSpin = function() {
    $('a#fetchallimages > i').removeClass("fa-refresh").addClass("fa-spinner fa-spin");
}

var setUpdateRefresh = function() {
    $('a#fetchallimages > i').removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-refresh");
}

var showEditView = function() {
    var editPane = $('#image-edit-content');
    editPane.empty();

    var imageContainer = $('<div class="image-container">');
    imageContainer.hide();

    var image = $('<img id="editing-image" class="edit-image">');
    image.attr("src", $(this).attr("data-image-url"));
    image.attr("data-image-id", $(this).attr("data-image-id"));

    editPane.append(imageContainer);
    imageContainer.append(image);


    // For reasons most speculative we need to give cropper some time to bind to the image.
    // Probably because the DOM hasn't been redrawn, and styles set
    setTimeout(function() {
        image.cropper({
            aspectRatio: 16/9,
            preview: "div > .image-edit-preview",
            autoCrop: true,
            dragCrop: true,
            modal: true,
            movable: true,
            resizable: true,
            zoomable: true,
            rotatable: false,
            multiple: false,
            done: function(data) {
                $('#cropperDataX').val(data.x);
                $('#cropperDataY').val(data.y);
                $('#cropperDataHeight').val(data.height);
                $('#cropperDataWidth').val(data.width);
            }
        });
        imageContainer.show();
    }, 400);
};


var updateAllUnhandledImages = function(unhandledImages) {
    var thumbnailContainer = $("#thumbnail-view");
    thumbnailContainer.empty();

    $.each(unhandledImages, function(index, value) {
        var imageThumbnail = $('<img class="thumbnail-image" data-toggle="tab" data-target="#edit-pane">');
        imageThumbnail.attr("src", value['thumbnail']);
        imageThumbnail.attr("data-image-id", value['id']);
        imageThumbnail.attr("data-image-url", value['image']);

        thumbnailContainer.append(imageThumbnail);
        imageThumbnail.on("click", showEditView);
    });
};


$("a#fetchallimages").click(function() {
    fetchUnhandledImages();
});

fetchUnhandledImages();

var crop_image = function() {
    var image = $('#editing-image');
    var cropData = image.cropper("getData");
    var imageId = image.attr("data-image-id");
    cropData.id = imageId;

    var request = $.post("crop_image", cropData, function() {
        console.log("success 1");
    })
        .done(function() {
            console.log("success 2");
        })
        .fail(function() {
            console.log("fail");
        })
        .always(function() {
            console.log("finished");
        });
};

$("#accept-crop-button").click(function() {
    crop_image();
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