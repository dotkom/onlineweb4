var Webshop = (function ($, tools) {
    var images;

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false;
        if ($ == undefined) {
            console.error('jQuery missing!');
            errors = true;
        }
        if (tools == undefined) {
            console.error('Dashboard tools missing!');
            errors = true;
        }
        if (errors) return false;
        return true;
    };

    var postDeleteForm = function (url) {
        $('<form method="POST" action="' + url + '">' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="' + 
        $('input[name=csrfmiddlewaretoken]').val() + '"></form>').submit();
    };

    return {

        // Bind them buttons and other initial functionality here
        init: function () {

            if (!performSelfCheck()) return;
            
            $('#webshop_product_list').tablesorter();
            $('#webshop_category_list').tablesorter();

            $('#webshop-delete-product').on('click', function (e) {
                e.preventDefault();
                $('.confirm-delete-product').data('slug', $(this).data('slug'));
            });

            $('.confirm-delete-product').on('click', function (e) {
                url = '/dashboard/webshop/product/' + $(this).data('slug') + '/delete';
                postDeleteForm(url);
            });

            $('#webshop-delete-category').on('click', function (e) {
                e.preventDefault();
                $('.confirm-delete-category').data('slug', $(this).data('slug'));
            });

            $('.confirm-delete-category').on('click', function (e) {
                url = '/dashboard/webshop/category/' + $(this).data('slug') + '/delete';
                postDeleteForm(url);
            });
        }

    };

})(jQuery, Dashboard.tools);

var WebshopGallery = (function ($, tools) {
    var images = [];
    var chosenList;

    var updateListImages = function() {
        chosenList.empty();
        for (var i = 0; i < images.length; i++) {
            var clone = $(images[i]).clone();
            // Remove on click
            clone.on('click', function() {
                removeImage(clone.context);
                
            });
            chosenList.append(clone);
        }
    };

    var addImage = function(image) {
        var $image = $(image);
        images.push(image);
        updateListImages();
        $image.addClass('image-selected');
    };

    var removeImage = function(image) {
        var $image = $(image);
        // Remove from list
        var index = images.indexOf(image);
        if(index > -1) {
            images.splice(index, 1);
        }
        updateListImages();
        $image.removeClass('image-selected');
    };

    var toggleImage = function(image) {
        var $image = $(image); // we php now
        var selected = $image.hasClass('image-selected');
        if(!selected) {
            addImage(image);
        }
        else {
            removeImage(image);
        }
        console.log(images);
    };

    return {
        init: function() {
            chosenList = $('#webshop-chosen-list');
            $('#webshop-image-list').on('click', 'img', function(e) {
                e.preventDefault();
                toggleImage(this);
            });
            chosenList.on('click', 'img', function(e) {
                e.preventDefault();
                removeImage(this);
            });
        }
    };
})(jQuery, Dashboard.tools);

$(document).ready(function () {
    Webshop.init();

    // Gallery image chooser
    if($('#webshop-image-list').size() > 0) {
        WebshopGallery.init();
    }
});
