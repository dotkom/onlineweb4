/*
 TODO: Automatically update the list of thumbnails when new images are uploaded, try to make it so that only the edited image is loaded to avoid unnecessary data traffic
 TODO: Add ajax method to fetch new images that are cropped and put them in the gallery, example in gallery.html
 TODO: Add support for tagging images
 TODO: Make the gallery prettier by framing stuff and allowing previews of different sizes
 */

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
        };

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


var clearMessage = function(id) {
    setTimeout(function() {
        var message = $('#' + id);
        message.fadeOut(1000, function() {
            $(this).remove();
        })
    }, 6000);
}

var createMessage = function(message) {
    var id = new Date().getTime();
    var messageElement = document.createElement("p");
    messageElement.setAttribute('id', id);
    messageElement.setAttribute('class', 'gallery-message');
    messageElement.innerHTML = message;
    clearMessage(id);
    return messageElement;
}

var setErrorMessage = function(message) {
    var messageElement = createMessage(message);
    messageElement.className += " " + 'text-danger' + " " + 'bg-danger';
    $('div#messages').append(messageElement);
}

var setSuccessMessage = function(message) {
    var messageElement = createMessage(message);
    messageElement.className += " " + 'text-success' + " " + 'bg-success';
    $('div#messages').append(messageElement);
}


var updateUneditedFiles = function() {
    $.ajax({
        method: 'GET',
        url: 'number_of_untreated',
        success: function(res) {
            var res = jQuery.parseJSON(res);
            var text = "Behandle (" + res['untreated'] + ")";
            $("#edit-button > div.caption").text(text);
        },
        crossDomain: false
    });
};

$(".bttrlazyloading").each(function() {
    $(this).bttrlazyloading(
        {
            container: '#gallery'
        }
    );
});


var fetchUnhandledImages = function() {
    setUpdateSpin();

    $.ajax({
        method: 'GET',
        url: 'get_all_untreated',
        success: function(res) {
            res = jQuery.parseJSON(res);
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
};

var setUpdateRefresh = function() {
    $('a#fetchallimages > i').removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-refresh");
};

var setCropSpin = function() {
    $('button#accept-crop-button > i').removeClass("fa-check").addClass("fa-spinner fa-spin");
};

var setCropDefault = function() {
    $('button#accept-crop-button > i').removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-check");
};

var clearEditView = function() {
    var editPane = $('#image-edit-content');
    var imageEditPreview = $("#image-edit-preview");
    editPane.empty();
    imageEditPreview.empty();
};


var showEditView = function() {
    clearEditView();

    var editPane = $('#image-edit-content');
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
            preview: "div > #image-edit-preview",
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


var getCurrentEditImageName = function() {
    var imageSrc = $('#editing-image').attr('src');
    return imageSrc.substring(imageSrc.lastIndexOf('/') + 1);

};


var getCurrentEditImageId = function() {
    return $('#editing-image').attr('data-image-id');
};


var imageEditingSuccessful = function() {

    var imageName = getCurrentEditImageName();
    var imageId = getCurrentEditImageId();
    var message = "Image '" + imageName + "' with id " + imageId + " was edited successfully!";

    setSuccessMessage(message);
    clearEditView();

    $('#showthumbnailpane').tab('show');
    fetchUnhandledImages();
};


var crop_image = function() {
    var image = $('#editing-image');
    var cropData = image.cropper("getData");
    cropData.id = image.attr("data-image-id");

    setCropSpin();

    $.post("crop_image", cropData, function() {
        imageEditingSuccessful();
    }).fail(function($xhr) {
        setErrorMessage($xhr.responseJSON);
    }).always(function() {
        setCropDefault();
    });
};

$("#accept-crop-button").click(function() {
    crop_image();
});


// Initial stuff

updateUneditedFiles();
fetchUnhandledImages();

setInterval(function() {
    updateUneditedFiles();
}, 3000);

// No idea what this does, but it made things work earlier
// Can probably be removed
new Blazy({
    container: '#edit-pane'
});