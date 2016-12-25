/*
    The Company module exposes functionality needed in the company section
    of the dashboard.
*/

var Inventory = (function ($, tools) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false
        if ($ == undefined) {
            console.error('jQuery missing!')
            errors = true
        }
        if (tools == undefined) {
            console.error('Dashboard tools missing!')
            errors = true
        }
        if (errors) return false
        return true
    }

    var postDeleteForm = function (url) {
        $('<form method="POST" action="' + url + '">' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="' +
        $('input[name=csrfmiddlewaretoken]').val() + '"></form>').submit()
    }

    return {

        // Bind them buttons and other initial functionality here
        init: function () {

            if (!performSelfCheck()) return

            $('#inventory-delete-item').on('click', function (e) {
                e.preventDefault()
                $('.confirm-delete-item').data('id', $(this).data('id'))
            })

            $('.deletebatch').on('click', function (e) {
                e.preventDefault()
                $('.confirm-delete-batch').data('id', $(this).data('id'))
            })

            $('.confirm-delete-item').on('click', function (e) {
                url = '/dashboard/inventory/item/' + $(this).data('id') + '/delete/'
                postDeleteForm(url)
            })

            $('.confirm-delete-batch').on('click', function (e) {
                url = '/dashboard/inventory/item/' +
                    $('#item_id').val() + '/batch/' + $(this).data('id') + '/delete/'
                postDeleteForm(url)
            })

            $('#inventory-add-batch').on('click', function (e) {
                e.preventDefault()
                $('#inventory-add-batch-form').slideToggle(200)
            })
        }

    }

})(jQuery, Dashboard.tools)


export default Inventory;
