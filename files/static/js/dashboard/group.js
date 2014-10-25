/*
    The Group module provides dynamic interaction with User and Group
    objects in the database, through AJAX POST.
*/

var Group = (function ($, tools) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false
        if ($ == undefined) console.error('jQuery missing!')
        if (tools == undefined) console.error('Dashboard tools missing!')
        if (errors) return false
        return true
    }

    // Private helper method to add a new user to table
    var add_user_to_table = function (fullname, id) {
        $('<tr>').html(
            '<td><a href="#">' + fullname + '</a><a href="#" id="' + id + 
            '" class="remove-user"><i class="fa fa-times fa-lg pull-right red">' +
            '</i></a></td>'
        ).appendTo($('#userlist'))
        
        var cell = $('#' + id).parent()
        $('#' + id).on('click', function (e) {
            e.preventDefault()
            Group.user.remove(id, cell)
        })

        // Sort the table again
        //tools.tablesort(document.getElementById('userlist'), 0)
    }

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
            if (action === 'remove_user') {
                row.fadeOut(200, function () {
                    row.remove()
                })
            }
            else if (action === 'add_user') {
                data = JSON.parse(data)
                add_user_to_table(data['full_name'], data['user_id'])
                tools.tablesort(document.getElementById('userlist'), 0)
            }
        }
        var error = function (xhr, txt, error) {
            tools.showStatusMessage(error, 'alert-danger')
        }

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', url, data, success, error, null)

    }

    return {

        // Bind them buttons here
        init: function () {

            if (!performSelfCheck()) return

            // Bind add users button
            $('#group_users_button').on('click', function (e) {
                e.preventDefault()
                $('#group_edit_users').slideToggle(200)
                $('#usersearch').focus()
            })
            
            // Bind remove user buttons
            $('.remove-user').each(function (i) {
                var cell = $(this).parent()
                var user_id = $(this).attr('id')
                $(this).on('click', function (e) {
                    e.preventDefault()
                    Group.user.remove(user_id, cell)
                })
            })
            
            /* Typeahead for user search */

            // Smart toggle function
            $.fn.toggleDisabled = function() {
                return this.each(function() {
                    this.disabled = !this.disabled
                })
            }

            // Typeahead template
            var user_search_template =  [
                '<span data-id="{{ id }}" class="user-meta"><h4>{{ name }}</h4>'
            ].join('')
            
            // Bind the input field
            $('#usersearch').typeahead({
                remote: "/profile/api_user_search/?query=%QUERY",
                updater: function (item) {
                    return item
                },
                template: user_search_template,
                engine: Hogan
            }).on('typeahead:selected typeahead:autocompleted', function(e, datum) {
                ($(function() {
                    Group.user.add(datum.id)
                }))
            })
        },

        // User module, has add and remove functions
        user: {
            remove: function (user_id, cell) {
                ajax_usermod(user_id, 'remove_user', cell.parent())
            },
            
            add: function (user_id) {
                ajax_usermod(user_id, 'add_user')
            }
        }
    }

})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Group.init()
})
