var Marks = (function ($, tools) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false
        if ($ == undefined) console.error('jQuery missing!')
        if (tools == undefined) console.error('Dashboard tools missing!')
        if (errors) return false
        return true
    }

    // Private generic ajax handler.
    // 
    // :param id: user ID in database
    // :param action: either 'remove_user' or 'add_user'
    var ajax_usermod = function (id, action) {
        var url = window.location.href.toString()
        var data = {
                "user_id": id,
                "action": action
        }
        var success = function (data) {
            if (action === 'remove_user') {
                data = JSON.parse(data)
                draw_table('userlist', data)
            }
            else if (action === 'add_user') {
                data = JSON.parse(data)
                draw_table('userlist', data)
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
            $('#marks_details_users_button').on('click', function (e) {
                e.preventDefault()
                $('#marks_details_users').slideToggle(200)
                $('#usersearch').focus()
            })
            
            // Bind remove user buttons
            $('.remove-user').each(function (i) {
                var cell = $(this).parent()
                var user_id = $(this).attr('id')
                $(this).on('click', function (e) {
                    e.preventDefault()
                    Marks.user.remove(user_id)
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
                    $('#usersearch').val('')
                }))
            })
        },

        // User module, has add and remove functions
        user: {
            remove: function (user_id, cell) {
                if (confirm('Er du sikker på at du vil fjerne prikken fra denne brukeren?')) {
                    ajax_usermod(user_id, 'remove_user')
                }
            },
            
            add: function (user_id) {
                ajax_usermod(user_id, 'add_user')
            }
        }
    }

})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Marks.init()
})
