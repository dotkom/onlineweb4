/*
    The Group module provides dynamic interaction with User and Group
    objects in the database, through AJAX POST.
*/

var Group = (function ($, tools) {

    // Private generic ajax handler.
    // 
    // :param id: user ID in database
    // :param action: either 'remove_user' or 'add_user'
    // :param row: the jQuery row object, so it can be faded out
    var ajax_usermod = function (id, action, row) {
        var url = window.location.href.toString()
        var data = {
                "user_id": id,
                "action": action
        }
        var success = function (data) {
            row.fadeOut(200, function () {
                row.remove()
            })
        }
        var error = function (xhr, txt, error) {
            tools.showStatusMessage(txt, 'alert-danger')
        }

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', url, data, success, error, null)

    }

    return {

        // Bind them buttons here
        init: function () {
            $('#group_users_button').on('click', function (e) {
                e.preventDefault()
                $('#group_edit_users').slideToggle(200)
            })

            $('.remove-user').each(function (i) {
                var cell = $(this).parent()
                var user_id = $(this).attr('id')
                $(this).on('click', function (e) {
                    e.preventDefault()
                    Group.user.remove(user_id, cell)
                })
            })
        },

        // User module, has add and remove functions
        user: {
            remove: function (user_id, cell) {
                ajax_usermod(user_id, 'remove_user', cell.parent())
            },
            
            add: function (id) {
                ajax_usermod(user_id, 'add_user', cell.parent())
            }
        }
    }

})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Group.init()
})
