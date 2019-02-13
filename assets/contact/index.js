import './less/contact.less';

document.getElementById('is_anon').addEventListener('click', () => {
  const checkbox = document.getElementById('id_contact_checkbox');
  const contactName = document.getElementById('id_contact_name');
  const contactMail = document.getElementById('id_contact_email');

  if (checkbox.checked) {
    contactMail.disabled = contactName.disabled = true;
  } else {
    contactMail.disabled = contactName.disabled = false;
  }
});
