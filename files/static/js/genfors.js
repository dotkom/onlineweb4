var Genfors;

Genfors = (function () {
    return {
        vote: (function () {
            return {
                bind_buttons: function () {
                    $('#verify_vote').on('click', function (e) {
                        e.preventDefault();
                        $('.voteverification').slideDown(200);
                        $('#verify_vote').addClass('disabled');
                    });
                    $('#cancel_vote').on('click', function (e) {
                        e.preventDefault();
                        $('.voteverification').slideUp(200);
                        $('#verify_vote').removeClass('disabled');
                    });
                },
            }
        }())
    }
}());

$(document).ready(function () {
    Genfors.vote.bind_buttons();
});
