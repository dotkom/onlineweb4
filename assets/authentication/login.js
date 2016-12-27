$(function() {
    // Setting focus on either username or password if errortext is presented
    if ($('#error_1_username').length > 0) {
        $('#username').focus();
    }
    else {
        if ($('#error_1_password').length > 0) {
            $('#password').focus();
        }
    }
});
