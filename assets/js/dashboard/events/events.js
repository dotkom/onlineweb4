import Hogan from 'hogan.js';
import jQuery from 'jquery';
/*
  The event module provides dynamic functions to event objects
  such as toggling paid, attended, adding and removing users on events
*/

const Event = (function PrivateEvent($, tools) {
  // Get the currently correct endpoint for posting user changes to
  const posOfLastSlash = window.location.href.toString().slice(0, window.location.href.toString().length).lastIndexOf('/');
  const attendanceEndpoint = `${window.location.href.toString().slice(0, posOfLastSlash)}/attendees/`;

  // Javascript to enable link to tab
  const url = document.location.toString();
  if (url.match('#')) {
    $(`.nav-tabs a[href="#${url.split('#')[1]}"]`).tab('show');
  }

  // Change hash for page-reload
  $('.nav-tabs a').on('shown.bs.tab', (e) => {
    if (history.pushState) {
      history.pushState(null, '', e.target.hash);
    } else {
      window.location.hash = e.target.hash; // Polyfill for old browsers
    }
  });

  const attendeeRow = (attendee) => {
    let row = '<tr>';
    row += `<td>${attendee.number}</td>`;
    row += `<td><a href="${attendee.link}">${attendee.first_name}</td>`;
    row += `<td><a href="${attendee.link}">${attendee.last_name}</td>`;
    // Paid cell
    row += `<td><a href="#" data-id="${attendee.id}" class="toggle-attendee paid">`;
    if (attendee.paid) {
      row += '<i class="fa fa-lg fa-check-square-o checked"></i>';
    } else {
      row += '<i class="fa fa-lg fa-square-o"></i>';
    }
    row += '</a></td>';
    // Attended cell
    row += `<td><a href="#" data-id="${attendee.id}" class="toggle-attendee attended">`;
    if (attendee.attended) {
      row += '<i class="fa fa-lg fa-check-square-o checked"></i>';
    } else {
      row += '<i class="fa fa-lg fa-square-o"></i>';
    }
    row += '</a></td>';
    // Extras cell
    row += `<td>${attendee.extras}</td>`;
    // Delete cell
    row += `<td><a href="#modal-delete-attendee" data-toggle="modal" data-id="${attendee.id}" class="remove-user">`;
    row += '<i class="fa fa-times fa-lg pull-right red"></i>';
    row += '</a></td>';
    // Close row
    row += '</tr>';
    return row;
  };

  const buttonBinds = () => {
    // Bind remove user buttons
    $('.remove-user').each(function removeUser() {
      $(this).on('click', function removeUserClick(e) {
        e.preventDefault();
        $('.modal-remove-user-name').text($(this).data('name'));
        $('.confirm-remove-user').data('id', $(this).data('id'));
      });
    });

    // Toggle paid and attended
    $('.toggle-attendee').each(function toggleAttendee() {
      $(this).on('click', function toggleAttendeeClick() {
        if ($(this).hasClass('attended')) {
          Event.attendee.toggle(this, 'attended');
        }
        if ($(this).hasClass('paid')) {
          Event.attendee.toggle(this, 'paid');
        }
      });
    });

    // Refresh tablesorter
    $('#attendees-table').trigger('update');
    $('#waitlist-table').trigger('update');
  };

  const drawTable = (tbody, data) => {
    // Redraw the table with new data
    let tbodyHtml = '';
    $.each(data, (i, attendee) => {
      tbodyHtml += attendeeRow(attendee);
    });
    $(`#${tbody}`).html(tbodyHtml);

    // Bind all the buttons
    buttonBinds();
  };

  return {

    // Bind them buttons here
    init() {
      $('#upcoming_events_list').tablesorter();
      $('#attendees-table').tablesorter();
      $('#waitlist-table').tablesorter();
      $('#extras-table').tablesorter();

      // Bind add users button
      $('#event_users_button').on('click', (e) => {
        e.preventDefault();
        $('#event_edit_users').slideToggle(200);
        $('#usersearch').focus();
      });

      // Bind toggle paid/attended and remove use button
      buttonBinds();

      // Bind the modal button only once
      $('.confirm-remove-user').on('click', function confirmRemoveUser() {
        Event.attendee.remove($(this).data('id'));
      });

      /* Typeahead for user search */

      // Typeahead template
      const userSearchTemplate = [
        '<span data-id="{{ id }}" class="user-meta"><h4>{{ value }}</h4>',
      ].join('');

      // Bind the input field
      $('#usersearch').typeahead({
        remote: '/profile/api_plain_user_search/?query=%QUERY',
        updater(item) {
          return item;
        },
        template: userSearchTemplate,
        engine: Hogan,
      }).on('typeahead:selected typeahead:autocompleted', (e, datum) => {
        ($(() => {
          Event.attendee.add(datum.id);
          $('#usersearch').val('');
        }));
      });
    },

    // Attendee module, toggles and adding
    attendee: {
      toggle(cell, action) {
        const data = {
          attendee_id: $(cell).data('id'),
          action,
        };
        const success = () => {
          // var line = $('#' + attendee_id > i)
          tools.toggleChecked(cell);
        };
        const error = (xhr, txt, errorMessage) => {
          tools.showStatusMessage(errorMessage, 'alert-danger');
        };

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', attendanceEndpoint, data, success, error, null);
      },
      add(userId) {
        const data = {
          user_id: userId,
          action: 'add_attendee',
        };
        const success = (eventData) => {
          $('#attendees-count').text(eventData.attendees.length);
          $('#waitlist-count').text(eventData.waitlist.length);
          // If this was the first attendee to be added we need to show the table
          if (eventData.attendees.length === 1) {
            $('#no-attendees-content').hide();
            $('#attendees-content').show();
          }
          // We have to redraw this table in any case
          drawTable('attendeelist', eventData.attendees);
          // Waitlist only needs to be considered if it actually has content
          if (eventData.waitlist.length > 0) {
            // If this was the first, etc
            if (eventData.waitlist.length === 1) {
              $('#no-waitlist-content').hide();
              $('#waitlist-content').show();
            }
            drawTable('waitlist', eventData.waitlist);
          }
          tools.showStatusMessage(data.message, 'alert-success');
        };
        const error = (xhr) => {
          tools.showStatusMessage(xhr.responseText, 'alert-danger');
        };

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', attendanceEndpoint, data, success, error, null);
      },
      remove(attendeeId) {
        const data = {
          attendee_id: attendeeId,
          action: 'remove_attendee',
        };
        const success = (eventData) => {
          $('#attendees-count').text(eventData.attendees.length);
          $('#waitlist-count').text(eventData.waitlist.length);
          // If there are no attendees left, hide the table
          if (eventData.attendees.length === 0) {
            $('#no-attendees-content').show();
            $('#attendees-content').hide();
          } else {
            // Only draw table if there are attendees to add to it
            drawTable('attendeelist', eventData.attendees);
          }
          // Hide waitlist if noone is in it.
          // Hard to do any checks to prevent doing this every time.
          if (eventData.waitlist.length === 0) {
            $('#no-waitlist-content').show();
            $('#waitlist-content').hide();
          } else {
            drawTable('waitlist', eventData.waitlist);
          }
          tools.showStatusMessage(eventData.message, 'alert-success');
        };
        const error = (xhr) => {
          tools.showStatusMessage(xhr.responseText, 'alert-danger');
        };

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', attendanceEndpoint, data, success, error, null);
      },

    },

  };
}(jQuery, window.Dashboard.tools));

jQuery(document).ready(() => {
  Event.init();
});
