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

    // Get the currently correct endpoint for posting user changes to
    var _pos_of_last_slash = window.location.href.toString().slice(0, window.location.href.toString().length).lastIndexOf('/')
    var attendance_endpoint = window.location.href.toString().slice(0, _pos_of_last_slash) + '/attendees/'

    // Javascript to enable link to tab
    var url = document.location.toString();
    if (url.match('#')) {
        $('.nav-tabs a[href="#' + url.split('#')[1] + '"]').tab('show');
    }

    // Change hash for page-reload
    $('.nav-tabs a').on('shown.bs.tab', function (e) {
        if(history.pushState) {
            history.pushState(null, "", e.target.hash);
        } else {
            window.location.hash = e.target.hash; //Polyfill for old browsers
        }
    })


    var draw_table = function (tbody, data) {
        // Redraw the table with new data
        var tbody_html = ''
        $.each(data, function (i, attendee) {
            tbody_html += attendee_row(attendee)
        })
        $('#' + tbody).html(tbody_html)

        // Bind all the buttons
        button_binds()
    }


    var attendee_row = function(attendee) {
        console.log(attendee)
        var row = '<tr>'
            row += '<td>'+ attendee.number +'</td>'
            row += '<td><a href="'+ attendee.link +'">'+ attendee.first_name +'</td>'
            row += '<td><a href="'+ attendee.link +'">'+ attendee.last_name +'</td>'
            // Paid cell
            row += '<td><a href="#" data-id="'+ attendee.id +'" class="toggle-attendee paid">'
            if (attendee.paid)
                row += '<i class="fa fa-lg fa-check-square-o checked"></i>'
            else
                row += '<i class="fa fa-lg fa-square-o"></i>'
            row += '</a></td>'
            // Attended cell
            row += '<td><a href="#" data-id="'+ attendee.id +'" class="toggle-attendee attended">'
            if (attendee.attended)
                row += '<i class="fa fa-lg fa-check-square-o checked"></i>'
            else
                row += '<i class="fa fa-lg fa-square-o"></i>'
            row += '</a></td>'
            // Extras cell
            row += '<td>' + attendee.extras +'</td>'
            // Delete cell
            row += '<td><a href="#modal-delete-attendee" data-toggle="modal" data-id="'+ attendee.id +'" class="remove-user">'
            row += '<i class="fa fa-times fa-lg pull-right red"></i>'
            row += '</a></td>'
            // Close row
            row += '</tr>'
        return row
    }

    var button_binds = function() {
        // Bind remove user buttons
        $('.remove-user').each(function (i) {
            $(this).on('click', function (e) {
                e.preventDefault()
                $('.modal-remove-user-name').text($(this).data('name'))
                $('.confirm-remove-user').data('id', $(this).data('id'))
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

        // Refresh tablesorter
        $('#attendees-table').trigger("update")
        $('#waitlist-table').trigger("update")
    }

    return {

        // Bind them buttons here
        init: function () {

            if (!performSelfCheck()) return

            $('#upcoming_events_list').tablesorter()
            $('#attendees-table').tablesorter()
            $('#waitlist-table').tablesorter()
            $('#extras-table').tablesorter()

            // Bind add users button
            $('#event_users_button').on('click', function (e) {
                e.preventDefault()
                $('#event_edit_users').slideToggle(200)
                $('#usersearch').focus()
            })

            // Bind toggle paid/attended and remove use button
            button_binds()

            // Bind the modal button only once
            $('.confirm-remove-user').on('click', function (e) {
                Event.attendee.remove($(this).data('id'))
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
                    Event.attendee.add(datum.id)
                    $('#usersearch').val('')
                }))
            })

        },

        // Attendee module, toggles and adding
        attendee: {
            toggle: function(cell, action) {
                var data = {
                    "attendee_id": $(cell).data('id'),
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
                tools.ajax('POST', attendance_endpoint, data, success, error, null)
            },
            add: function(user_id) {
                var data = {
                    "user_id": user_id,
                    "action": "add_attendee"
                }
                var success = function (data) {
                    $('#attendees-count').text(data.attendees.length)
                    $('#waitlist-count').text(data.waitlist.length)
                    // If this was the first attendee to be added we need to show the table
                    if (data.attendees.length === 1) {
                        $('#no-attendees-content').hide()
                        $('#attendees-content').show()
                    }
                    // We have to redraw this table in any case
                    draw_table('attendeelist', data.attendees)
                    // Waitlist only needs to be considered if it actually has content
                    if (data.waitlist.length > 0) {
                        // If this was the first, etc
                        if (data.waitlist.length === 1) {
                            $('#no-waitlist-content').hide()
                            $('#waitlist-content').show()
                        }
                        draw_table('waitlist', data.waitlist)
                    }
                    tools.showStatusMessage(data.message, 'alert-success')
                }
                var error = function (xhr, txt, error) {
                    tools.showStatusMessage(xhr.responseText, 'alert-danger')
                }

                // Make an AJAX request using the Dashboard tools module
                tools.ajax('POST', attendance_endpoint, data, success, error, null)
            },
            remove: function(attendee_id) {
                var data = {
                    "attendee_id": attendee_id,
                    "action": "remove_attendee"
                }
                var success = function (data) {
                    $('#attendees-count').text(data.attendees.length)
                    $('#waitlist-count').text(data.waitlist.length)
                    // If there are no attendees left, hide the table
                    if (data.attendees.length === 0) {
                        $('#no-attendees-content').show()
                        $('#attendees-content').hide()
                    }
                    // Only draw table if there are attendees to add to it
                    else {
                        draw_table('attendeelist', data.attendees)
                    }
                    // Hide waitlist if noone is in it. Hard to do any checks to prevent doing this every time.
                    if (data.waitlist.length === 0) {
                        $('#no-waitlist-content').show()
                        $('#waitlist-content').hide()
                    }
                    else {
                        draw_table('waitlist', data.waitlist)
                    }
                    tools.showStatusMessage(data.message, 'alert-success')
                }
                var error = function (xhr, txt, error) {
                    tools.showStatusMessage(xhr.responseText, 'alert-danger')
                }

                // Make an AJAX request using the Dashboard tools module
                tools.ajax('POST', attendance_endpoint, data, success, error, null)
            },

        }

    }


})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Event.init()
})
