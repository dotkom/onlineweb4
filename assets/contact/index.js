import './less/contact.less';

const checkbox = document.getElementById('id_contact_checkbox');
checkbox.addEventListener('change', () => {
  const contactName = document.getElementById('id_contact_name');
  const contactMail = document.getElementById('id_contact_email');

  if (checkbox.checked) {
    contactMail.disabled = contactName.disabled = true;
  } else {
    contactMail.disabled = contactName.disabled = false;
  }
});
