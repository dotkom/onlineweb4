import jQuery from 'jquery';
import { plainUserTypeahead } from 'common/typeahead';
import { ajax, showStatusMessage } from 'common/utils';

/*
    The Group module provides dynamic interaction with User and Group
    objects in the database, through AJAX POST.
*/

const Group = (function PrivateGroup($) {
  const bindButtonListeners = () => {
    $('.remove-user').each(function removeUser() {
      const userId = $(this).attr('id');
      $(this).on('click', (e) => {
        e.preventDefault();
        Group.user.remove(userId);
      });
    });

    $('.toggle-on-leave').each(function toggleOnLeave() {
      const memberId = $(this).attr('data-id');
      $(this).on('click', (e) => {
        e.preventDefault();
        Group.user.toggleOnLeave(memberId);
      });
    });

    $('.toggle-retired').each(function toggleRetired() {
      const memberId = $(this).attr('data-id');
      $(this).on('click', (e) => {
        e.preventDefault();
        Group.user.toggleRetired(memberId);
      });
    });

    $('.add-role').each(function addRole() {
      const userId = $(this).attr('data-user-id');
      const roleId = $(this).attr('data-role-id');
      $(this).on('click', (e) => {
        e.preventDefault();
        Group.user.addRole(userId, roleId);
      });
    });

    $('.remove-role').each(function removeRole() {
      const userId = $(this).attr('data-user-id');
      const roleId = $(this).attr('data-role-id');
      $(this).on('click', (e) => {
        e.preventDefault();
        Group.user.removeRole(userId, roleId);
      });
    });
  };

  const handleError = (xhr, txt, errorMessage) => {
    const message = xhr.responseText || errorMessage;
    showStatusMessage(message, 'alert-danger');
  };

  // Private helper method to draw the user table
  //
  // :param tbody: the ID of the <tbody> element of the table
  // :param data: the JSON parsed data returned by the server
  const drawTable = (tbody, data) => {
    let tbodyHtml = '';
    data.members.forEach((member) => {
      tbodyHtml += `
        <tr>
          <td>
            <a href="#">${member.full_name}</a>
          </td>
          <td>
            <div class="btn-group">
             ${member.roles.map(role => `
               <button type="button" class="btn btn-labeled btn-primary remove-role" data-role-id="${role.id}" data-user-id="${member.user_id}">
                 <span class="btn-label"><i class="glyphicon glyphicon-remove"></i></span>${role.verbose_name}
               </button>
             `).join('')}
              <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="caret"></span>
                <span class="sr-only">Legg til rolle</span>
              </button>
              <ul class="dropdown-menu">
                 ${data.group_roles.map(role => `
                   <li><a href="#" class="add-role" data-user-id="${member.user_id}" data-role-id="${role.id}">${role.verbose_name}</a></li>
                 `).join('')}
              </ul>
            </div>
          </td>
          <td>
            <a href="#" data-id="${member.id}" data-value="${member.is_on_leave}" class="toggle-on-leave">
              <i class="fa fa-lg ${member.is_on_leave ? 'fa-check-square-o checked' : 'fa-square-o'}"></i>
            </a>
          </td>
          <td>
            <a href="#" data-id="${member.id}" data-value="${member.is_retired}" class="toggle-retired">
              <i class="fa fa-lg ${member.is_retired ? 'fa-check-square-o checked' : 'fa-square-o'}"></i>
            </a>
          </td>
          <td>
            <a href="#" id="${member.user_id}" class="remove-user">
              <i class="fa fa-times fa-lg pull-right red"></i>
            </a>
          </td>
        </tr>
      `;
    });
    $(`#${tbody}`).html(tbodyHtml);
    bindButtonListeners();
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

    ajax('POST', url, data, success, handleError, null);
  };

  const ajaxRolemod = (userId, roleId, action) => {
    const url = window.location.href.toString();
    const data = {
      user_id: userId,
      role_id: roleId,
      action,
    };
    const success = (responseData) => {
      if (action === 'remove_role' || action === 'add_role') {
        drawTable('userlist', JSON.parse(responseData));
      }
    };

    ajax('POST', url, data, success, handleError, null);
  };

  const ajaxToggleRetired = (memberId) => {
    const url = `/api/v1/group/members/${memberId}/`;
    const element = document.querySelector(`[data-id="${memberId}"][class="toggle-retired"]`);
    const [icon] = element.getElementsByTagName('i');
    const currentValue = element.dataset.value === 'true';
    const data = {
      is_retired: !currentValue,
    };
    const success = (member) => {
      const classes = `fa fa-lg ${member.is_retired ? 'fa-check-square-o checked' : 'fa-square-o'}`;
      element.dataset.value = member.is_retired;
      icon.className = classes;
    };

    ajax('PATCH', url, data, success, handleError, null);
  };

  const ajaxToggleOnLeave = (memberId) => {
    const url = `/api/v1/group/members/${memberId}/`;
    const element = document.querySelector(`[data-id="${memberId}"][class="toggle-on-leave"]`);
    const [icon] = element.getElementsByTagName('i');
    const currentValue = element.dataset.value === 'true';
    const data = {
      is_on_leave: !currentValue,
    };
    const success = (member) => {
      const classes = `fa fa-lg ${member.is_on_leave ? 'fa-check-square-o checked' : 'fa-square-o'}`;
      element.dataset.value = member.is_on_leave;
      icon.className = classes;
    };

    ajax('PATCH', url, data, success, handleError, null);
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

      bindButtonListeners();

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

      toggleOnLeave(memberId) {
        ajaxToggleOnLeave(memberId);
      },

      toggleRetired(memberId) {
        ajaxToggleRetired(memberId);
      },

      addRole(userId, roleId) {
        ajaxRolemod(userId, roleId, 'add_role');
      },

      removeRole(userId, roleId) {
        ajaxRolemod(userId, roleId, 'remove_role');
      },
    },
  };
}(jQuery));

jQuery(document).ready(() => {
  Group.init();
});
