import jQuery from 'jquery';
import { plainUserTypeahead } from 'common/typeahead';
import { ajax, showStatusMessage } from 'common/utils';

/*
    The Group module provides dynamic interaction with User and Group
    objects in the database, through AJAX POST.
*/

const Group = (function PrivateGroup($) {
  // Private helper method to draw the user table
  //
  // :param tbody: the ID of the <tbody> element of the table
  // :param data: the JSON parsed data returned by the server
  const drawTable = (tbody, data) => {
    let tbodyHtml = '';
    $(data.users).each((i) => {
      tbodyHtml += `
        <tr>
          <td>
            <a href="#">${data.users[i].user}</a>
            <a href="#" id="user_${data.users[i].id}" class="remove-user">
              <i class="fa fa-times fa-lg pull-right red"></i>
            </a>
          </td>
        </tr>
      `;
    });
    $(`#${tbody}`).html(tbodyHtml);

    $(data.users).each((i) => {
      const user = data.users[i];
      $(`#user_${user.id}`).on('click', (e) => {
        e.preventDefault();
        Group.user.remove(user.id);
      });
    });
  };

  // Private generic ajax handler.
  //
  // :param id: user ID in database
  // :param action: either 'remove_user' or 'add_user'
  const ajaxUsermod = (id, action) => {
    const url = window.location.href.toString();
    const data = {
      user_id: id,
      action,
    };
    const success = (responseData) => {
      if (action === 'remove_user' || action === 'add_user') {
        drawTable('userlist', JSON.parse(responseData));
      }
    };
    const error = (xhr, txt, errorMessage) => {
      showStatusMessage(errorMessage, 'alert-danger');
    };

    ajax('POST', url, data, success, error, null);
  };

  return {

    // Bind them buttons here
    init() {
      // Bind add users button
      $('#group_users_button').on('click', (e) => {
        e.preventDefault();
        $('#group_edit_users').slideToggle(200);
        $('#usersearch').focus();
      });

      // Bind remove user buttons
      $('.remove-user').each(function removeUser() {
        const userId = $(this).attr('id');
        $(this).on('click', (e) => {
          e.preventDefault();
          Group.user.remove(userId);
        });
      });

      /* Typeahead for user search */
      plainUserTypeahead($('#usersearch'), (e, datum) => {
        ($(() => {
          Group.user.add(datum.id);
          $('#usersearch').val('');
        }));
      });
    },

    // User module, has add and remove functions
    user: {
      remove(userId) {
        if (confirm('Er du sikker på at du vil fjerne brukeren fra gruppen?')) {
          ajaxUsermod(userId, 'remove_user');
        }
      },

      add(userId) {
        ajaxUsermod(userId, 'add_user');
      },
    },
  };
}(jQuery));

jQuery(document).ready(() => {
  Group.init();
});
