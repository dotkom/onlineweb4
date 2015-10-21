var Webshop = (function ($, tools) {

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

$(document).ready(function () {
    Webshop.init();
});
