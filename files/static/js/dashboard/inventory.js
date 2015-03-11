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

    var add_batch_to_item = function () {
        var url = window.location.href.toString() + 'batch/'
        var data = {
            "amount": $('#inventory-batch-amount').val(),
            "expiry": $('#inventory-batch-expiry').val(),
            "action": "add"
        }
        var success = function (data) {
            $('#inventory-batch-list tbody').append(
                $('<tr>').html(
                    '<td>' + data['amount'] + '</td>' +
                    '<td>' + data['expiry'] + '</td>' +
                    '<td><a href="#" class="delete-batch" id="' +
                    data['id'] + '">' + 
                    '<i class="fa fa-times fa-lg red"></a>'
                )
            )

            $('#inventory-batch-amount').val(0)
            $('#inventory-batch-expiry').val('')

            $('#' + data['id']).on('click', function (e) {
                e.preventDefault()
                delete_batch(data['id'], $(this).parent().parent())
            })

            tools.showStatusMessage('Batchen ble lagt til.', 'alert-success')
        }
        var error = function (xhr, txt, error) {
            tools.showStatusMessage(xhr.responseText, 'alert-danger')
        }

        tools.ajax('POST', url, data, success, error, null)
    }

    var delete_batch = function (id, tr) {
        var url = window.location.href.toString() + 'batch/'
        var data = {
            "action": "delete",
            "id": id
        }
        var success = function (data) {
            $(tr).remove()
            tools.showStatusMessage('Batchen ble fjernet.', 'alert-success')
        }
        var error = function (xhr, txt, error) {
            tools.showStatusMessage(xhr.responseText, 'alert-danger')
        }

        tools.ajax('POST', url, data, success, error, null)
    }

    return {

        // Bind them buttons and other initial functionality here
        init: function () {

            if (!performSelfCheck()) return
            
            $('#inventory_item_list').tablesorter()

            $('#inventory-batch-list').tablesorter()

            $('#inventory-delete-item').on('click', function (e) {
                e.preventDefault()
                if (confirm('Er du sikker på at du vil slette denne varen?')) {
                    window.location = this.href
                }
            })

            $('#inventory-add-batch').on('click', function (e) {
                e.preventDefault()
                $('#inventory-add-batch-form').slideToggle(200)
            })

            $('#inventory-save-batch').on('click', function (e) {
                e.preventDefault()
                add_batch_to_item()
            })

            $('.delete-batch').on('click', function (e) {
                e.preventDefault()
                delete_batch(this.id, $(this).parent().parent())
            })
        }

    }

})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Inventory.init()
})
