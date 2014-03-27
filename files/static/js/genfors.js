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
                    $('#toggle_vote_code').on('click', function (e) {
                        var self = $(this);
                        var span = $('#vote_code');
                        if(!span.is(':visible')) {
                            span.show();
                            self.text('Skjul stemmekode');
                        }
                        else {
                            span.hide();
                            self.text('Vis stemmekode');
                        }
                    });
                },
            }
        }())
    }
}());

$(document).ready(function () {
    Genfors.vote.bind_buttons();
});
