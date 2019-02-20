import './less/contact.less';

const checkbox = document.getElementById('id_contact_checkbox');
const contactName = document.getElementById('id_contact_name');
const contactMail = document.getElementById('id_contact_email');

checkbox.addEventListener('change', () => {
  contactMail.disabled = checkbox.checked;
  contactMail.value = '';

  contactName.disabled = checkbox.checked;
  contactName.value = '';
});
