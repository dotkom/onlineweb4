import './less/contact.less';

document.getElementById("is_anon").addEventListener("click", () => {

    const checkbox = document.getElementById("id_contact_checkbox");
    const contact_name = document.getElementById("id_contact_name");
    const contact_mail = document.getElementById("id_contact_email");

    if (checkbox.checked) {
        contact_mail.disabled = contact_name.disabled= true;
    }
    else {
        contact_mail.disabled = contact_name.disabled = false;
    }
})