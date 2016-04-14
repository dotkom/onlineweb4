var Genfors;

Genfors = (function () {

    var DEBUG = false

    var ACTIVE_QUESTION = null

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
                    $('input[name=choice]:radio').change(function (e) {
                        e.preventDefault();
                        $('.voteverification').slideUp(200);
                        $('#verify_vote').removeClass('disabled');
                    });
                },
            }
        }()),

        update: function () {
            $.getJSON("/genfors/api/user", function (data) {
                if (DEBUG) console.log("Update cycle...")
                // Is this the first run after page load?
                if (ACTIVE_QUESTION === null) {
                    if (DEBUG) console.log("First run after pageload.")
                    // Is there an active question?
                    if (data.question !== null) {
                        // Set the flag to true
                        ACTIVE_QUESTION = true
                        if (DEBUG) console.log("We have an active question, updating flag.")
                    }
                    else {
                        // We do not have an active question, set flag and return
                        ACTIVE_QUESTION = false
                        if (DEBUG) console.log("We do not have an active question, updating flag.")
                        return
                    }
                // Do we have an active question?
                } else if (ACTIVE_QUESTION === true) {
                    // If we have an active question, but it has now been closed, reload
                    if (DEBUG) console.log("We have an active question.")
                    if (data.question === null) {
                        if (DEBUG) console.log("Question close detected, reloading page.")
                        window.location.reload()
                        return
                    }
                // We do not have an active question
                } else if (ACTIVE_QUESTION === false) {
                    if (DEBUG) console.log("We do not have an active question.")
                    // We did not have an active question, but now have one, reload
                    if (data.question !== null) {
                        if (DEBUG) console.log("New question detected, reloading page.")
                        window.location.reload()
                    }
                    // Else just return
                    else return
                }

                if ('total_voter' in data.question) {
                    $('#total_voters').text(data.question.total_voters);
                }
                if ('current_votes' in data.question) {
                    $('#current_vote_count').text(data.question.current_votes);
                }
                var votes_html = "";
                data.question.votes.sort();
                if ('votes' in data.question) {
                    for (var x = 0; x < data.question.votes.length; x++) {
                        votes_html += '<li>' + data.question.votes[x][0];
                        var v = data.question.votes[x][1];
                        if (v === true || v === false || v === null) {
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
                                votes_html += '<span title="'+ v +'" class="label label-primary pull-right">'+ v.substring(0,20);
                                if (v.length > 20) votes_html += '…';
                                votes_html += '</span></li>';
                            }
                        }
                    }
                    $('#votes').html(votes_html);
                }
                if ('results' in data.question) {
                    var r = data.question.results.data;
                    var blank = r['Blankt'];
                    var votes_for_alternative = data.question.current_votes - blank;
                    if ('Ja' in r || 'Nei' in r) {
                        var yes = r['Ja'];
                        var no = r['Nei'];
                        var current_votes = data.question.current_votes;
                        var options = Object.keys(r);
                        options.sort(function(a,b) {return r[b]-r[a]});
                        options = Genfors.blank_at_bottom(options);
                        var html = "";
                        for (var x = 0; x < options.length; x++) {
                            var key = options[x];
                            var value = r[key];
                            var percent;
                            if (data.question.count_blank_votes) {
                                percent = Genfors.get_percent(value, current_votes);
                                html += '<p><strong>' + key + '</strong>: ' + value + ' stemme' + ((value>1)?'r':'') + '</p>';
                            }
                            else {
                                if (key == 'Blankt') {
                                    percent = Genfors.get_percent(value, current_votes);
                                    html += '<p class="p-blank"><strong>' + key + ' (ikke tellende)</strong>: ' + value + ' stemme' + ((value>1)?'r':'') + '</p>';
                                }
                                else{
                                    percent = Genfors.get_percent(value, votes_for_alternative);
                                    html += '<p><strong>' + key + '</strong>: ' + value + ' stemme' + ((value>1)?'r':'') + '</p>';
                                }
                            }
                            type = "";
                            if (data.question.count_blank_votes) {
                                if (key == 'Ja') {
                                    type = 'success';
                                }
                                else if (key == 'Nei') {
                                    type = 'danger';
                                }
                                else {
                                    type = 'warning';
                                }
                                html += '<div class="progress"><div class="progress-bar progress-bar-' + type +'" role="progressbar" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%">' + percent + '%</div></div>';
                            }
                            else {
                                if (key == 'Blankt') { 
                                    type = 'warning';
                                    html += '<div class="progress"><div class="progress-bar progress-bar-' + type + '" role="progressbar" aria-valuenow="' + percent + 
                                        '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%;">' + value + ' av ' + current_votes + 
                                        ' stemme' + ((current_votes>1)?'r':'') + '</div></div>';
                                }
                                else {
                                    if (key == 'Ja') {
                                        type = 'success';
                                    }
                                    else if (key == 'Nei') {
                                        type = 'danger';
                                    }
                                    html += '<div class="progress"><div class="progress-bar progress-bar-' + type +'" role="progressbar" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%;">' + percent + '%</div></div>';
                                }
                            }
                        }
                        $('#bool_progress').html(html);
                    }
                    else {
                        var alternatives = Object.keys(r);
                        alternatives.sort(function(a,b){return r[b]-r[a]});
                        alternatives = Genfors.blank_at_bottom(alternatives);
                        var current_votes = data.question.current_votes;
                        var html = "";
                        for (var x = 0; x < alternatives.length; x++) {
                            var key = alternatives[x];
                            var value = r[key];
                            var percent;
                            if (key == 'Blankt' && !data.question.count_blank_votes) {
                                percent = Genfors.get_percent(value, current_votes);
                                html += '<p class="p-blank"><strong>' + key + ' (ikke tellende)</strong>: ' + value + ' stemme' + ((value>1)?'r':'') + '</p>';
                            }
                            else{
                                percent = Genfors.get_percent(value, votes_for_alternative);
                                html += '<p><strong>' + key + '</strong>: ' + value + ' stemme' + ((value>1)?'r':'') + '</p>';
                            }
                            if (data.question.count_blank_votes) {
                                percent = Genfors.get_percent(value, current_votes);
                                type = "primary";
                                html += '<div class="progress"><div class="progress-bar progress-bar-' + type + '" role="progressbar" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%">' + percent + '%</div></div>';
                            }
                            else {
                                if (key == 'Blankt') {
                                    percent = Genfors.get_percent(value, current_votes);
                                    type = "warning";
                                    html += '<div class="progress"><div class="progress-bar progress-bar-' + type + '" role="progressbar" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%">' + value + ' av ' + current_votes + ' stemme' + ((current_votes>1)?'r':'') + 
                                        '</div></div>';
                                }
                                else {
                                    percent = Genfors.get_percent(value, votes_for_alternative);
                                    type = "primary";
                                    html += '<div class="progress"><div class="progress-bar progress-bar-' + type + '" role="progressbar" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + percent + '%">' + percent + '%</div></div>';
                                }
                            }
                        }
                        $('#mc_progress').html(html);
                    }
                }
                //console.log(new Date() + ': Fetched stats from genfors API.');
            });
        },

        get_percent: function (votes, total) {
            return Math.floor(votes * 100 / total) || 0;
        },

        blank_at_bottom: function (alternatives) {
            for (var i = 0; i < alternatives.length; i++) {
                if (alternatives[i] == 'Blankt') {
                    alternatives.unshift(alternatives.splice(i, 1));
                    return alternatives.reverse();
                }
            }
            return null;
        }
    }
}());

$(document).ready(function () {
    Genfors.vote.bind_buttons();
    setInterval(Genfors.update, 10000);
});
