import './less/contact.less';

const checkbox = document.getElementById('id_contact_checkbox');
const contactName = document.getElementById('id_contact_name');
const contactMail = document.getElementById('id_contact_email');

contactMail.required = contactName.required = true;

checkbox.addEventListener('change', () => {
  if (checkbox.checked) {
    contactMail.disabled = contactName.disabled = true;
  } else {status
    contactMail.disabled = contactName.disabled = false;
  }
});
