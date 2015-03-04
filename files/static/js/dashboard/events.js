/*
    The event module provides dynamic functions to event objects
    such as toggling paid, attended, adding and removing users on events
*/

var Event = (function ($, tools) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false
        if ($ == undefined) console.error('jQuery missing!')
        if (tools == undefined) console.error('Dashboard tools missing!')
        if (errors) return false
        return true
    }


    var draw_table = function (tbody, data) {
        var tbody_html = ''
        $(data.users).each(function (i) {
            tbody_html += attendee_row(data.users[i].id)
        })
        $('#' + tbody).html(tbody_html)
        
        $(data.users).each(function (i) {
            var user = data.users[i]
            $('#user_' + user.id).on('click', function (e) {
                e.preventDefault()
                Event.user.remove(user.id)
            })
        })
    }


    var attendee_row = function(attendee_id) {
        var row = '<tr>' + 
                    '<td><a href="{% url dashboard_attendee_details attendee.id %}">{{ attendee }}</a></td>' +
                    '<td>' +
                        '<a href="#" id="{{ attendee.id }}" class="toggle-attendee paid">' +
                            '<i class="fa fa-lg {% if attendee.paid %}fa-check-square-o green{% else %}fa-square-o red{% endif %}"></i>' +
                        '</a>' +
                    '</td>' +
                    '<td>' +
                        '<a href="#" id="{{ attendee.id }}" class="toggle-attendee attended">' +
                            '<i class="fa fa-lg {% if attendee.attended %}fa-check-square-o green{% else %}fa-square-o red{% endif %}"></i>' +
                        '</a>' +
                    '</td>' +
                '</tr>'
        return row
    }

    return {

        // Bind them buttons here
        init: function () {

            if (!performSelfCheck()) return

            $('#upcoming_events_list').tablesorter()
            $('#event_attendee_list').tablesorter()

            // Bind add users button
            $('#event_users_button').on('click', function (e) {
                e.preventDefault()
                $('#event_edit_users').slideToggle(200)
                $('#usersearch').focus()
            })

            // Bind remove user buttons
            $('.remove-user').each(function (i) {
                var cell = $(this).parent()
                var user_id = $(this).attr('id')
                $(this).on('click', function (e) {
                    e.preventDefault()
                    Group.user.remove(user_id)
                })
            })
            
            // Toggle paid and attended
            $('.toggle-attendee').each(function (i) {
                $(this).on('click', function (e) {
                    if ($(this).hasClass('attended')) {
                        Event.attendee.toggle(this, 'attended')
                    }
                    if ($(this).hasClass('paid')) {
                        Event.attendee.toggle(this, 'paid')
                    }
                })
            })

            /* Typeahead for user search */

            // Typeahead template
            var user_search_template =  [
                '<span data-id="{{ id }}" class="user-meta"><h4>{{ value }}</h4>'
            ].join('')

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
                    Events.attendee.add(datum.id)
                    $('#usersearch').val('')
                }))
            })

        },

        // Attendee module, toggles and adding
        attendee: {
            toggle: function(cell, action) {
                var url = window.location.href.toString()
                var attendee_id = $(cell).attr('id')
                var data = {
                        "attendee_id": attendee_id,
                        "action": action
                }
                var success = function (data) {
                    //var line = $('#' + attendee_id > i)
                    tools.toggleChecked(cell)
                }
                var error = function (xhr, txt, error) {
                    tools.showStatusMessage(error, 'alert-danger')
                }

                // Make an AJAX request using the Dashboard tools module
                tools.ajax('POST', url, data, success, error, null)
            },
            add: function(user_id) {
                var url = window.location.href.toString()
                var data = {
                        "user_id": user_id,
                        "action": "add"
                }
            },
        }

    }
    
    
})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Event.init()
})
