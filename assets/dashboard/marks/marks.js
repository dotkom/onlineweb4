import jQuery from 'jquery';
import { plainUserTypeahead } from 'common/typeahead';

const Marks = (function PrivateMarks($, tools) {
  // Private helper method to draw the user table
  //
  // :param tbody: the ID of the <tbody> element of the table
  // :param data: the JSON parsed data returned by the server
  const drawTable = (tbody, data) => {
    let tbodyHtml = '';
    $(data.mark_users).each((i) => {
      tbodyHtml += `
        <tr>
          <td>
            <a href="#">${data.mark_users[i].user}</a>
            <a href="#" id="user_${data.mark_users[i].id}" class="remove-user">
              <i class="fa fa-times fa-lg pull-right red"></i>
            </a>
          </td>
        </tr>`;
    });
    $(`#${tbody}`).html(tbodyHtml);

    $(data.mark_users).each((i) => {
      const user = data.mark_users[i];
      $(`#user_${user.id}`).on('click', (e) => {
        e.preventDefault();
        Marks.user.remove(user.id);
      });
    });
  };

  // Private generic ajax handler.
  //
  // :param id: user ID in database
  // :param action: either 'remove_user' or 'add_user'
  const ajaxUsermod = (id, action) => {
    const url = window.location.href.toString();
    const postData = {
      user_id: id,
      action,
    };
    const success = (data) => {
      if (action === 'remove_user' || action === 'add_user') {
        const jsonData = JSON.parse(data);
        const mark = jsonData.mark;

        drawTable('userlist', jsonData);
        tools.showStatusMessage(jsonData.message, 'alert-success');

        $('#dashboard-marks-changed-by').html(mark.last_changed_by);
        $('#dashboard-marks-changed-time').html(mark.last_changed_date);
      }
    };
    const error = (xhr) => {
      const response = jQuery.parseJSON(xhr.responseText);
      tools.showStatusMessage(response.message, 'alert-danger');
    };

    // Make an AJAX request using the Dashboard tools module
    tools.ajax('POST', url, postData, success, error, null);
  };

  return {

    // Bind them buttons here
    init() {
      // Bind add users button
      $('#marks_details_users_button').on('click', (e) => {
        e.preventDefault();
        $('#marks_details_users').slideToggle(200);
        $('#usersearch').focus();
      });

      // Bind remove user buttons
      $('.remove-user').each(function removeUser() {
        const userId = $(this).attr('id');
        $(this).on('click', (e) => {
          e.preventDefault();
          Marks.user.remove(userId);
        });
      });

      /* Typeahead for user search */
      plainUserTypeahead($('#usersearch'), (e, datum) => {
        ($(() => {
          Marks.user.add(datum.id);
          $('#usersearch').val('');
        }));
      });
    },

    // User module, has add and remove functions
    user: {
      remove(userId) {
        if (confirm('Er du sikker på at du vil fjerne prikken fra denne brukeren?')) {
          ajaxUsermod(userId, 'remove_user');
        }
      },

      add(userId) {
        ajaxUsermod(userId, 'add_user');
      },
    },
  };
}(jQuery, window.Dashboard.tools));


export default Marks;
