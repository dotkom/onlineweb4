var Marks = (function ($, tools) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false;
        if ($ == undefined) console.error('jQuery missing!');
        if (tools == undefined) console.error('Dashboard tools missing!');
        if (errors) return false;
        return true
    };

    // Private helper method to draw the user table
    //
    // :param tbody: the ID of the <tbody> element of the table
    // :param data: the JSON parsed data returned by the server
    var draw_table = function (tbody, data) {
        var tbody_html = '';
        $(data.mark_users).each(function (i) {
            tbody_html += '<tr><td><a href="#">' + data.mark_users[i].user + '</a>' +
                          '<a href="#" id="user_' + data.mark_users[i].id + '" class="remove-user">' +
                          '<i class="fa fa-times fa-lg pull-right red">' + '</i></a></td></tr>';
        });
        $('#' + tbody).html(tbody_html);

        $(data.mark_users).each(function (i) {
            var user = data.mark_users[i];
            $('#user_' + user.id).on('click', function (e) {
                e.preventDefault();
                Marks.user.remove(user.id);
            })
        })
    };

    // Private generic ajax handler.
    // 
    // :param id: user ID in database
    // :param action: either 'remove_user' or 'add_user'
    var ajax_usermod = function (id, action) {
        var url = window.location.href.toString();
        var data = {
                "user_id": id,
                "action": action
        };
        var success = function (data) {
            if (action === 'remove_user') {
                data = JSON.parse(data);
                draw_table('userlist', data);
                tools.showStatusMessage(data.message, 'alert-success');
            }
            else if (action === 'add_user') {
                data = JSON.parse(data);
                draw_table('userlist', data);
                tools.showStatusMessage(data.message, 'alert-success');
            }

            if (action == 'remove_user' || action == 'add_user') {
                $('#dashboard-marks-changed-by').html(data.mark.last_changed_by);
                $('#dashboard-marks-changed-time').html(data.mark.last_changed_date);
            }
        };
        var error = function (xhr, txt, error) {
            var response = jQuery.parseJSON(xhr.responseText);
            tools.showStatusMessage(response.message, 'alert-danger');
        };

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', url, data, success, error, null);
    };

    return {

        // Bind them buttons here
        init: function () {

            if (!performSelfCheck()) return;

            $('#marks_list').tablesorter();

            // Bind add users button
            $('#marks_details_users_button').on('click', function (e) {
                e.preventDefault();
                $('#marks_details_users').slideToggle(200);
                $('#usersearch').focus();
            });
            
            // Bind remove user buttons
            $('.remove-user').each(function (i) {
                var cell = $(this).parent();
                var user_id = $(this).attr('id');
                $(this).on('click', function (e) {
                    e.preventDefault();
                    Marks.user.remove(user_id);
                })
            });
            
            /* Typeahead for user search */

            // Smart toggle function
            $.fn.toggleDisabled = function() {
                return this.each(function() {
                    this.disabled = !this.disabled
                })
            };

            // Typeahead template
            var user_search_template =  [
                '<span data-id="{{ id }}" class="user-meta"><h4>{{ value }}</h4>'
            ].join('');
            
            // Bind the input field
            $('#usersearch').typeahead({
                remote: "/profile/api_plain_user_search/?query=%QUERY",
                updater: function (item) {
                    return item
                },
                template: user_search_template,
                engine: Hogan
            }).on('typeahead:selected typeahead:autocompleted', function(e, datum) {
                ($(function() {
                    Marks.user.add(datum.id);
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

})(jQuery, Dashboard.tools);

$(document).ready(function () {
    Marks.init();
});
