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
        }()),

        update: function () {
            $.getJSON("/genfors/api/user", function (data) {
                if ('total_voters' in data) {
                    $('#total_voters').text(data.question.total_voters);
                }
                if ('current_votes' in data.question) {
                    $('#current_vote_count').text(data.question.current_votes);
                }
                var votes_html = "";
                if ('votes' in data.question) {
                    for (var x = 0; x < data.question.votes.length; x++) {
                        votes_html += '<li>' + data.question.votes[x][0];
                        var v = data.question.votes[x][1];
                        if (v == true || v == false || v == null) {
                            if (v) {
                                votes_html += '<span class="label label-success pull-right">Ja</span></li>';
                            }
                            else if (v == false) {
                                votes_html += '<span class="label label-danger pull-right">Nei</span></li>';
                            }
                            else {
                                votes_html += '<span class="label label-warning pull-right">Blankt</span></li>';
                            }
                        }
                        else {
                            if (v == 'Blankt') {
                                votes_html += '<span class="label label-warning pull-right">' + v + '</span></li>';
                            }
                            else {
                                votes_html += '<span class="label label-primary pull-right">' + v + '</span></li>';
                            }
                        }
                    }
                    $('#votes').html(votes_html);
                }
                if ('results' in data.question) {
                    var r = data.question.results.data;
                    if ('Ja' in r || 'Nei' in r) {
                        var yes = r['Ja']
                        var no = r['Nei']
                        var blank = r['Blankt']
                        var current_votes = data.question.current_votes;
                        var options = Object.keys(r);
                        options.sort(function(a,b) {return r[b]-r[a]});
                        var html = "";
                        for (var x = 0; x < options.length; x++) {
                            var key = options[x];
                            var value = r[key];
                            var percent = Genfors.get_percent(value, current_votes);
                            html += '<strong>' + key + '</strong>: ' + value + ' stemme';
                            if (value != 1) {
                                html += 'r';
                            }
                            type = "";
                            if (key == 'Ja') {
                                type = 'success';
                            }
                            else if (key == 'Nei') {
                                type = 'danger';
                            }
                            else {
                                type = 'warning';
                            }
                            html += '<p /><div class="progress"><div class="progress-bar progress-bar-' + type +'" role="progressbar" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%">' + percent + '%</div></div>';
                        }
                        $('#bool_progress').html(html);
                    }
                    else {
                        var alternatives = Object.keys(r);
                        alternatives.sort(function(a,b){return r[b]-r[a]});
                        var current_votes = data.question.current_votes;
                        var html = "";
                        for (var x = 0; x < alternatives.length; x++) {
                            var key = alternatives[x];
                            var value = r[key];
                            var percent = Genfors.get_percent(value, current_votes);
                            html += '<strong>' + key + '</strong>: ' + value + ' stemme';
                            if (value != 1) {
                                html += 'r';
                            }
                            type = "primary";
                            html += '<p /><div class="progress"><div class="progress-bar progress-bar-"' + type + ' role="progressbar" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%">' + percent + '%</div></div>';
                        }
                        $('#mc_progress').html(html);
                    }
                }
                //console.log(new Date() + ': Fetched stats from genfors API.');
            });
        },

        get_percent: function (votes, total) {
            return Math.floor(votes * 100 / total);
        }
    }
}());

$(document).ready(function () {
    Genfors.vote.bind_buttons();
    setInterval(Genfors.update, 10000);
});
