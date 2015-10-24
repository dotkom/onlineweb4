/*
 * Gallery.js is included in Dashboard by default.
 *
 * To utilize, either include gallery/formwidget.html for ModelForms,
 * or gallery/widget.html for use outside forms.
 */

var Gallery = (function ($, tools) {

    var currentPage = 1;
    var currentImages = [];
    var minResolution = [1280, 720];

    var singleSelectedImage = null;

    // Binds all buttons and event listeners as well as
    // lazyloading for images
    var bindEventListeners = function () {

        $("#image-input").change(function() {
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

        $(".bttrlazyloading").each(function() {
            $(this).bttrlazyloading(
                {
                    container: '#gallery'
                }
            );
        });

        $("#accept-crop-button").on('click', function(e) {
            e.preventDefault();
            crop_image();
        });

        $("#fetchallimages").click(function() {
            fetchUnhandledImages();
        });

        $('#add-responsive-image').on('click', function (e) {
            e.preventDefault()
            $('#image-upload-wrapper').hide()
            $('#image-selection-wrapper').slideToggle(200, function () {
                $('#image-gallery-search').focus()
            })
        })

        $('#upload-responsive-image').on('click', function (e) {
            e.preventDefault()
            $('#image-selection-wrapper').hide()
            $('#image-upload-wrapper').slideToggle(200, function () {
                window.location.href = '#image-gallery-title'
            })
        })

        var searchImages = function (query) {
            payload = { query: query }
            tools.ajax('GET', '/gallery/search/', payload, function (data) {
                console.log(data)
                var html = '';
                for (var i = 0; i < data.images.length; i++) {

                    html += '<div class="col-md-6 col-sm-12 col-xs-12">'
                    html +=   '<div class="image-selection-thumbnail" data-id="' + data.images[i].id + '">'
                    html +=     '<div class="image-selection-thumbnail-image">'
                    html +=       '<img src="' + data.images[i].thumbnail + '" title="' + data.images[i].name + '">'
                    html +=     '</div>'
                    html +=     '<div class="image-selection-thumbnail-text">'
                    html +=       '<h4 class="image-title">' + data.images[i].name + '</h4>'
                    html +=       '<span class="image-timestamp">' + data.images[i].timestamp + '</span>'
                    html +=       '<p class="image-description">' + data.images[i].description +'</p>'
                    html +=     '</div>'
                    html +=   '</div>'
                    html += '</div>'
                }
                if (!data.images.length) html = '<div class="col-md-12"><p>Ingen bilder matchet søket...</p></div></div>'
                else html += '</div>'
                $('#image-gallery-search-results').html(html)

                // Creates click listeners for all the newly added image tiles
                bindSingleImageSelectionListeners();

            }, function (xhr, thrownError, statusText) {
                alert(thrownError)
            })
        }
        $('#image-gallery-search').on('keypress', function (e) {
            if (e.keyCode === 13) {
                e.preventDefault();
                e.stopPropagation();
                searchImages($(this).val())
            }
        })
        $('#image-gallery-search-button').on('click', function(e) {
            e.preventDefault()
            searchImages($('#image-gallery-search').val())
        })
    }

    /**
     * Binds click selection listeners to all responsive image thumbnails for single image
     * selection. On click, the selectSingleImage call on the widget module will
     * fetch the ID from the data attribute on the DOM element, and update the hidden form field
     * containing the value.
     */
    function bindSingleImageSelectionListeners() {
        $('.image-selection-thumbnail').on('click', function (e) {
            Gallery.widget.selectSingleImage($(this))
        })
    }

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

    var clearMessage = function(id) {
        setTimeout(function() {
            var message = $('#' + id);
            message.fadeOut(200, function() {
                $(this).remove();
            })
        }, 5000);
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
            url: '/gallery/number_of_untreated/',
            success: function(res) {
                var res = jQuery.parseJSON(res);
                var text = "Behandle (" + res['untreated'] + ")";
                $("#edit-button > div.caption").text(text);
            },
            crossDomain: false
        });
    };

    var fetchUnhandledImages = function() {
        setUpdateSpin();

        $.ajax({
            method: 'GET',
            url: '/gallery/get_all_untreated/',
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
        $('#fetchallimages > i').removeClass("fa-refresh").addClass("fa-spinner fa-spin");
    };

    var setUpdateRefresh = function() {
        $('#fetchallimages > i').removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-refresh");
    };

    var setCropSpin = function() {
        $('#accept-crop-button > i').removeClass("fa-check").addClass("fa-spinner fa-spin");
    };

    var setCropDefault = function() {
        $('#accept-crop-button > i').removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-check");
    };

    var clearEditView = function() {
        var editPane = $('#image-edit-content')
        var imageEditPreview = $("#image-edit-preview")
        var editName = $('#image-edit-name')
        var editDescription = $('#image-edit-description')
        editPane.empty();
        imageEditPreview.empty();
        editName.val('');
        editDescription.val('');
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
                preview: ".image-edit-preview",
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
        var message = "Bilde '" + imageName + "' med id " + imageId + " ble lagret!";

        setSuccessMessage(message);
        clearEditView();

        $('#showthumbnailpane').tab('show');
        fetchUnhandledImages();
    };


    var crop_image = function() {
        var image = $('#editing-image');
        var cropData = image.cropper("getData");
        var image_name = $('#image-edit-name');
        var image_description = $('#image-edit-description');
        cropData.name = image_name.val();
        cropData.description = image_description.val();

        if (cropData.name.length < 2) {
            alert('Du må gi bildet et navn!');
            image_name.focus();
            return;
        }
        if (cropData.width < minResolution[0] || cropData.height < minResolution[1]) {
            return alert('Utsnittet er for lite. Det må være minst 1024x768');
        }

        cropData.id = image.attr("data-image-id");

        setCropSpin();

        $.post("/gallery/crop_image/", cropData, function() {
            imageEditingSuccessful();
        }).fail(function($xhr) {
            setErrorMessage($xhr.responseJSON);
        }).always(function() {
            setCropDefault();
        });
    };

    return {
        init: function () {
            if ($('#image-upload-wrapper').length || $('#image-selection-wrapper').length) {

                $.ajaxSetup({
                    crossDomain: false, // obviates need for sameOrigin test
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type)) {
                            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                        }
                    }
                });

                // Initial stuff
                bindEventListeners();
                updateUneditedFiles();
                fetchUnhandledImages();

                setInterval(function() {
                    updateUneditedFiles();
                }, 3000);

                if (window.location.href.indexOf('#manage-pane') != -1) {
                    $('#edit-button').click()
                }
            }
        },
        widget: {
            selectSingleImage: function (imageDOMelement) {
                if (singleSelectedImage) singleSelectedImage.removeClass('image-selection-thumbnail-active')
                singleSelectedImage = imageDOMelement;
                singleSelectedImage.addClass('image-selection-thumbnail-active')
                inputValue = $('#responsive-image-id')
                thumbnailWrapper = $('#single-image-field-thumbnail')
                if (inputValue.length) {
                    inputValue.val(singleSelectedImage.attr('data-id'))
                    thumbnailWrapper.html('<img src="' + singleSelectedImage.find('img').attr('src') + '" alt>')
                }
            }
        }
    }
})(jQuery, Dashboard.tools)

Gallery.init()
