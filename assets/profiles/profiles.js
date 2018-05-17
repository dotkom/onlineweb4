import $ from 'jquery';
import { ajaxEnableCSRF, setStatusMessage } from 'common/utils/';

ajaxEnableCSRF($);

$(document).ready(() => {
  // Generic javascript to enable interactive tabs that do not require page reload
  const switchTab = (newActiveTab) => {
    if ($('#profile-tabs').length) {
      const tabElement = $('#profile-tabs').find(`[data-section="${newActiveTab}"]`);
      if (tabElement.length) {
        // Hide sections
        $('#tab-content section').hide();
        // Unmark currently active tab
        $('#profile-tabs').find('li.active').removeClass('active');
        // Update the active tab to the clicked tab and show that section
        tabElement.parent().addClass('active');
        $(`#${newActiveTab}`).show();
        // Update URL
        window.history.pushState({}, document.title, $(tabElement).attr('href'));
      }
    }
  };

  // Hide all other tabs and show the active one when the page loads
  if ($('#profile-tabs').length) {
    // Hide all sections
    $('#tab-content section').hide();
    // Find the currently active tab and show it
    const activeTab = $('#profile-tabs').find('li.active a').data('section');
    $(`#${activeTab}`).show();

    // Set up the tabs to show/hide when clicked
    $('#profile-tabs').on('click', 'a', function tabClick(e) {
      e.preventDefault();
      const newActiveTab = $(this).data('section');
      switchTab(newActiveTab);
    });
  }

  // Fix for tabs when going 'back' in the browser history
  window.addEventListener('popstate', () => {
    // If you can figure out how to do this properly, be my guest.
  });

  function animatePrivacyBox(checkbox, state) {
    if (state) {
      $(checkbox).removeClass('on');
      $(checkbox).addClass('off');
    } else {
      $(checkbox).removeClass('off');
      $(checkbox).addClass('on');
    }
  }

  $('.privacybox').click(function privacyBoxClick() {
    const checkbox = $(this).find('input');
    const checked = checkbox.is(':checked');
    checkbox.prop('checked', !checked);

    animatePrivacyBox(this, checked);
  });

  // Popover for privacy and user image
  $('#privacy-help').popover({ placement: 'bottom' });
  $('#image-help').popover({ placement: 'bottom' });

  /*
   JS for marks pane
  */
  const updateMarkRules = () => {
    $.ajax({
      method: 'POST',
      url: 'update_mark_rules/',
      data: { rules_accepted: true },
      success(res) {
        const jsonResponse = JSON.parse(res);
        setStatusMessage(jsonResponse.message, 'alert-success');
        $('.marks').attr('disabled', true);
      },
      error() {
        setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
      },
      crossDomain: false,
    });
  };

  function performMarkRulesClick() {
    const markscheckbox = $('#marks-checkbox');
    const checked = markscheckbox.is(':checked');
    markscheckbox.prop('checked', !checked);

    if (!checked) {
      $('.marks').removeClass('off').addClass('on');
      updateMarkRules();
    }
  }

  $('.marks').mouseup(() => {
    if (!($('#marks-checkbox').is(':checked'))) {
      performMarkRulesClick();
    }
  });

  $('#marks-checkbox').click((e) => {
    e.stopPropagation();
    e.preventDefault();
  });

  /*
   JS for email management.
  */

  $('button.add-new-email').click(function addNewEmail() {
    $('div.new-email-form').show();
    $(this).hide();
  });
  $('.emptyonclick').focus(function emptyonclick() {
    $(this).val('');
  });

  const deleteEmail = (email, row) => {
    $.ajax({
      method: 'POST',
      url: 'delete_email/',
      data: { email },
      success() {
        // TODO Make animation
        $(row).hide();
      },
      error(res) {
        if (res.status === 412) {
          const jsonResponse = JSON.parse(res.responseText);
          setStatusMessage(jsonResponse.message, 'alert-danger');
        } else {
          setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
        }
      },
      crossDomain: false,
    });
  };

  const setPrimaryEmail = (email, row) => {
    $.ajax({
      method: 'POST',
      url: 'set_primary/',
      data: { email },
      success() {
        $('button.active').removeClass('active')
          .removeClass('btn-success')
          .addClass('btn-default')
          .prop('disabled', false)
          .text('Sett primær');
        $(row).find('button.primary')
          .addClass('active')
          .removeClass('btn-default')
          .addClass('btn-success')
          .prop('disabled', true)
          .text('Primær');
      },
      error(res) {
        if (res.status === 412) {
          const jsonResponse = JSON.parse(res.responseText);
          setStatusMessage(jsonResponse.message, 'alert-danger');
        } else {
          setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
        }
      },
      crossDomain: false,
    });
  };

  const verifyEmail = (email) => {
    $.ajax({
      method: 'POST',
      url: 'verify_email/',
      data: { email },
      success() {
        setStatusMessage(`En ny verifikasjonsepost har blitt sendt til ${email}.`, 'alert-success');
      },
      error(res) {
        if (res.status === 412) {
          const jsonResponse = JSON.parse(res.responseText);
          setStatusMessage(jsonResponse.message, 'alert-danger');
        } else {
          setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
        }
      },
      crossDomain: false,
    });
  };


  $('div.email-row').each((i, row) => {
    // Ajax request to delete an email
    $(row).find('button.delete').click(() => {
      const email = $(row).find('p.email').text();
      deleteEmail(email, row);
    });
    // Ajax request to set email as primary
    $(row).find('button.primary').click(() => {
      const email = $(row).find('p.email').text();
      setPrimaryEmail(email, row);
    });
    // Ajax request to send verification mail
    $(row).find('button.verify').click(() => {
      const email = $(row).find('p.email').text();
      verifyEmail(email, row);
    });
  });

  const toggleSubscription = (list) => {
    // Dispatch event allowing IsLoading component to show.
    document.dispatchEvent(new Event('ow4-long-xhr-start'));

    const listID = $(`#toggle_${list}`);
    $.ajax({
      method: 'POST',
      url: `toggle_${list}/`,
      data: {},
      success(data) {
        // Tell IsLoading-component that request ended.
        document.dispatchEvent(new Event('ow4-long-xhr-end'));

        const res = JSON.parse(data);
        if (res.state === true) {
          listID.removeClass('btn-success');
          listID.addClass('btn-danger');
          listID.text('Deaktivér');
        } else {
          listID.removeClass('btn-danger');
          listID.addClass('btn-success');
          listID.text('Aktivér');
        }
      },
      error() {
        // Tell IsLoading-component that request ended.
        document.dispatchEvent(new Event('ow4-long-xhr-end'));

        setStatusMessage('Det oppstod en uventet feil under endring.', 'alert-danger');
      },
      crossDomain: false,
    });
  };

  const infomail = $('#toggle_infomail');
  infomail.on('click', (e) => {
    e.preventDefault();
    toggleSubscription('infomail');
  });

  const jobmail = $('#toggle_jobmail');
  jobmail.on('click', (e) => {
    e.preventDefault();
    toggleSubscription('jobmail');
  });

  $('.delete-position').on('click', function deletePosition(e) {
    const that = $(this);
    e.preventDefault();
    $.ajax({
      method: 'post',
      url: '/profile/deleteposition/',
      data: { position_id: $(this).data('position-id') },
      success(res) {
        const result = JSON.parse(res);
        $(that).parent().remove();
        setStatusMessage(result.message, 'alert-success');
      },
      error(res) {
        const result = JSON.parse(res);
        if (res.status === 500) {
          setStatusMessage(result.message, 'alert-danger');
        }
      },
      crossDomain: false,
    });
  });
});
