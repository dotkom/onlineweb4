import jQuery from 'jquery';
import { plainUserTypeahead } from 'common/typeahead';
import { ajax, showStatusMessage, setChecked } from 'common/utils';
import { element } from 'prop-types';
import bootstrapTabJs from 'common/bootstrap-tab';

bootstrapTabJs(jQuery);

/*
  The event module provides dynamic functions to event objects
  such as toggling paid, attended, adding and removing users on events
*/

const Event = (function PrivateEvent($) {
  // Get the currently correct endpoint for posting user changes to
  const posOfLastSlash = window.location.href
        .toString()
        .slice(0, window.location.href.toString().length)
        .lastIndexOf('/');
  const attendanceEndpoint = `${window.location.href
        .toString()
        .slice(0, posOfLastSlash)}/attendees/`;

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

  const attendeeRow = (attendee, isPaymentEvent, hasExtras) => {
    let row = '<tr role="row">';
    row += `<td>${attendee.number}</td>`;
    row += `<td><a href="${attendee.link}">${attendee.first_name}</a></td>`;
    row += `<td><a href="${attendee.link}">${attendee.last_name}</a></td>`;
    row += `<td><a href="${attendee.link}">${attendee.year_of_study}</a></td>`;

    // Paid cell
    if (isPaymentEvent) {
      row += `<td class="paid-container">
                <a href="#" data-id="${attendee.id}" class="toggle-attendee paid">`;
      if (attendee.paid) {
        row += '<i class="fa fa-lg fa-check-square-o checked"></i>';
      } else {
        row += '<i class="fa fa-lg fa-square-o"></i>';
      }
      row += `</a><div>${attendee.payment_deadline}</div></td>`;
    }
    // Attended cell
    row += `<td><a href="#" data-id="${attendee.id}" class="toggle-attendee attended">`;

    if (attendee.attended) {
      row += '<i class="fa fa-lg fa-check-square-o checked"></i>';
    } else {
      row += '<i class="fa fa-lg fa-square-o"></i>';
    }
    row += '</a></td>';

    // Extras cell
    if (hasExtras) {
      row += `<td>${(!attendee.extras || attendee.extras === 'None' ? '-' : attendee.extras)}</td>`;
    } else {
      row += `<td>${(!attendee.allergies || attendee.allergies === 'None' ? '-' : attendee.allergies)}</td>`;
    }

    // Delete cell
    row += `<td><a href="#modal-delete-attendee" data-toggle="modal" data-id="${attendee.id}" data-name="${attendee.first_name} ${attendee.last_name}" class="remove-user">`;
    row += '<i class="fa fa-times fa-lg red"></i>';
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
    $('.toggle-attendee').each(function toggleAttendee(_, elem) {
      let checked = Boolean(elem.querySelector(".checked"));
      $(this).on('click', function toggleAttendeeClick(e) {
        e.preventDefault();
        checked = !checked;
        if ($(this).hasClass('attended')) {
          Event.attendee.setChecked(this, 'attended', checked);
        }
        if ($(this).hasClass('paid')) {
          Event.attendee.setChecked(this, 'paid', checked);
        }
      });
    });

    // Refresh tablesorter
    $('#attendees-table').trigger('update');
    $('#waitlist-table').trigger('update');
  };

  const drawTable = (tbody, data, isPaymentEvent, hasExtras) => {
    // Redraw the table with new data
    let tbodyHtml = '';
    $.each(data, (i, attendee) => {
      tbodyHtml += attendeeRow(attendee, isPaymentEvent, hasExtras);
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
      plainUserTypeahead($('#usersearch'), (e, datum) => {
        $(() => {
          Event.attendee.add(datum.id);
          $('#usersearch').val('');
        });
      });
    },

    // Attendee module, toggles and adding
    attendee: {
      setCheckedXhr: null,
      setChecked(cell, action, checked) {
        const data = {
          attendee_id: $(cell).data('id'),
          action,
          value: checked,
        };
        const success = (eventData) => {
          drawTable('attendeelist', eventData.attendees, eventData.is_payment_event, eventData.has_extras);
        };
        let originalChecked = Boolean(cell.querySelector(".checked"));
        const error = (error) => {
          if (error.statusText !== 'abort') {
            showStatusMessage(error.statusText, 'alert-danger');
            setChecked(cell, originalChecked);
          }
        };

        setChecked(cell, checked);
        if (this.setCheckedXhr) {
          this.setCheckedXhr.abort();
        }
        this.setCheckedXhr = ajax('POST', attendanceEndpoint, data, success, error, null);
        console.log(this.setCheckedXhr)
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
          drawTable('attendeelist', eventData.attendees, eventData.is_payment_event, eventData.has_extras);
          // Waitlist only needs to be considered if it actually has content
          if (eventData.waitlist.length > 0) {
            // If this was the first, etc
            if (eventData.waitlist.length === 1) {
              $('#no-waitlist-content').hide();
              $('#waitlist-content').show();
            }
            drawTable('waitlist', eventData.waitlist, eventData.is_payment_event, eventData.has_extras);
          }
          showStatusMessage(eventData.message, 'alert-success');
        };
        const error = (xhr) => {
          showStatusMessage(xhr.responseText, 'alert-danger');
        };

        ajax('POST', attendanceEndpoint, data, success, error, null);
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
            drawTable('attendeelist', eventData.attendees, eventData.is_payment_event, eventData.has_extras);
          }
          // Hide waitlist if noone is in it.
          // Hard to do any checks to prevent doing this every time.
          if (eventData.waitlist.length === 0) {
            $('#no-waitlist-content').show();
            $('#waitlist-content').hide();
          } else {
            drawTable('waitlist', eventData.waitlist, eventData.is_payment_event, eventData.has_extras);
          }
          showStatusMessage(eventData.message, 'alert-success');
        };
        const error = (xhr) => {
          showStatusMessage(xhr.responseText, 'alert-danger');
        };

        ajax('POST', attendanceEndpoint, data, success, error, null);
      },
    },
  };
}(jQuery));

jQuery(document).ready(() => {
  Event.init();
});
