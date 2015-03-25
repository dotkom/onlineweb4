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

            $('.deletebatch').on('click', function (e) {
                if (confirm('Er du sikker på at du vil slette denne batchen?')) {
                    // STUB
                } else {
                    e.preventDefault()
                }
            })

            $('.datepicker').on('click', function (e) {
                e.preventDefault()
                alert('Datepicker er ikke implementert enda. Kommer snart(tm)!')
            })
        }

    }

})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Inventory.init()
})
