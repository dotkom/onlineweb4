import $ from 'jquery';

const Genfors = (function PrivateGenfors() {
  const DEBUG = false;

  let ACTIVE_QUESTION = null;

  return {
    vote: {
      bind_buttons() {
        $('#verify_vote').on('click', (e) => {
          e.preventDefault();
          $('.voteverification').slideDown(200);
          $('#verify_vote').addClass('disabled');
        });
        $('#cancel_vote').on('click', (e) => {
          e.preventDefault();
          $('.voteverification').slideUp(200);
          $('#verify_vote').removeClass('disabled');
        });
        $('#toggle_vote_code').on('click', function toggleVoteCode() {
          const self = $(this);
          const span = $('#vote_code');
          if (!span.is(':visible')) {
            span.show();
            self.text('Skjul stemmekode');
          } else {
            span.hide();
            self.text('Vis stemmekode');
          }
        });
        $('input[name=choice]:radio').change((e) => {
          e.preventDefault();
          $('.voteverification').slideUp(200);
          $('#verify_vote').removeClass('disabled');
        });
      },
    },

    update() {
      $.getJSON('/genfors/api/user', (data) => {
        if (DEBUG) console.log('Update cycle...');
        // Is this the first run after page load?
        if (ACTIVE_QUESTION === null) {
          if (DEBUG) console.log('First run after pageload.');
          // Is there an active question?
          if (data.question !== null) {
            // Set the flag to true
            ACTIVE_QUESTION = true;
            if (DEBUG) console.log('We have an active question, updating flag.');
          } else {
            // We do not have an active question, set flag and return
            ACTIVE_QUESTION = false;
            if (DEBUG) console.log('We do not have an active question, updating flag.');
            return;
          }
        // Do we have an active question?
        } else if (ACTIVE_QUESTION === true) {
          // If we have an active question, but it has now been closed, reload
          if (DEBUG) console.log('We have an active question.');
          if (data.question === null) {
            if (DEBUG) console.log('Question close detected, reloading page.');
            window.location.reload();
            return;
          }
        // We do not have an active question
        } else if (ACTIVE_QUESTION === false) {
          if (DEBUG) console.log('We do not have an active question.');
          // We did not have an active question, but now have one, reload
          if (data.question !== null) {
            if (DEBUG) console.log('New question detected, reloading page.');
            window.location.reload();
          } else {
            return;
          }
        }

        if ('total_voter' in data.question) {
          $('#total_voters').text(data.question.total_voters);
        }
        if ('current_votes' in data.question) {
          $('#current_vote_count').text(data.question.current_votes);
        }
        let votesHtml = '';
        data.question.votes.sort();
        if ('votes' in data.question) {
          for (let x = 0; x < data.question.votes.length; x += 1) {
            votesHtml += `<li>${data.question.votes[x][0]}`;
            const v = data.question.votes[x][1];
            if (v === true || v === false || v === null) {
              if (v) {
                votesHtml += '<span class="label label-success pull-right">Ja</span></li>';
              } else if (v === false) {
                votesHtml += '<span class="label label-danger pull-right">Nei</span></li>';
              } else {
                votesHtml += '<span class="label label-warning pull-right">Blankt</span></li>';
              }
            } else if (v === 'Blankt') {
              votesHtml += `<span class="label label-warning pull-right">${v}</span></li>`;
            } else {
              votesHtml += `<span title="${v}" class="label label-primary pull-right">${v.substring(0, 20)}`;
              if (v.length > 20) votesHtml += '…';
              votesHtml += '</span></li>';
            }
          }
          $('#votes').html(votesHtml);
        }
        if ('results' in data.question) {
          const r = data.question.results.data;
          const blank = r.Blankt;
          const votesForAlternative = data.question.current_votes - blank;
          if ('Ja' in r || 'Nei' in r) {
            const currentVotes = data.question.current_votes;
            let options = Object.keys(r);
            options.sort((a, b) => r[b] - r[a]);
            options = Genfors.blank_at_bottom(options);
            let html = '';
            for (let x = 0; x < options.length; x += 1) {
              const key = options[x];
              const value = r[key];
              let percent;
              if (data.question.count_blank_votes) {
                percent = Genfors.get_percent(value, currentVotes);
                html += `<p><strong>${key}</strong>: ${value} stemme${(value > 1) ? 'r' : ''}</p>`;
              } else if (key === 'Blankt') {
                percent = Genfors.get_percent(value, currentVotes);
                html += `<p class="p-blank"><strong>${key} (ikke tellende)</strong>: ${value} stemme${(value > 1) ? 'r' : ''}</p>`;
              } else {
                percent = Genfors.get_percent(value, votesForAlternative);
                html += `<p><strong>${key}</strong>: ${value} stemme${(value > 1) ? 'r' : ''}</p>`;
              }
              let type = '';
              if (data.question.count_blank_votes) {
                if (key === 'Ja') {
                  type = 'success';
                } else if (key === 'Nei') {
                  type = 'danger';
                } else {
                  type = 'warning';
                }
                html += `
                  <div class="progress">
                    <div
                      class="progress-bar progress-bar-${type}" role="progressbar"
                      aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"
                      style="width: ${percent}%"
                    >
                      ${percent}%
                    </div>
                  </div>`;
              } else if (key === 'Blankt') {
                type = 'warning';
                html += `
                  <div class="progress">
                    <div
                      class="progress-bar progress-bar-${type}" role="progressbar"
                      aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"
                      style="width: ${percent}%;"
                    >
                      ${value} av ${currentVotes} stemme${(currentVotes > 1) ? 'r' : ''}
                    </div>
                  </div>`;
              } else {
                if (key === 'Ja') {
                  type = 'success';
                } else if (key === 'Nei') {
                  type = 'danger';
                }
                html += `
                  <div class="progress">
                    <div
                      class="progress-bar progress-bar-${type}" role="progressbar"
                      aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"
                      style="width: ${percent}%;"
                    >
                      ${percent}%
                    </div>
                  </div>`;
              }
            }
            $('#bool_progress').html(html);
          } else {
            let alternatives = Object.keys(r);
            alternatives.sort((a, b) => r[b] - r[a]);
            alternatives = Genfors.blank_at_bottom(alternatives);
            const currentVotes = data.question.current_votes;
            let html = '';
            for (let x = 0; x < alternatives.length; x += 1) {
              const key = alternatives[x];
              const value = r[key];
              if (key === 'Blankt' && !data.question.count_blank_votes) {
                html += `
                  <p class="p-blank">
                    <strong>${key} (ikke tellende)</strong>: ${value} stemme${(value > 1) ? 'r' : ''}
                  </p>`;
              } else {
                html += `
                  <p>
                    <strong>${key}</strong>: ${value} stemme${(value > 1) ? 'r' : ''}
                  </p>`;
              }
              if (data.question.count_blank_votes) {
                const percent = Genfors.get_percent(value, currentVotes);
                const type = 'primary';
                html += `<div class="progress"><div class="progress-bar progress-bar-${type}" role="progressbar" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100" style="width: ${percent}%">${percent}%</div></div>`;
              } else if (key === 'Blankt') {
                const percent = Genfors.get_percent(value, currentVotes);
                const type = 'warning';
                html += `<div class="progress"><div class="progress-bar progress-bar-${type}" role="progressbar" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100" style="width: ${percent}%">${value} av ${currentVotes} stemme${(currentVotes > 1) ? 'r' : ''
                                        }</div></div>`;
              } else {
                const percent = Genfors.get_percent(value, votesForAlternative);
                const type = 'primary';
                html += `<div class="progress"><div class="progress-bar progress-bar-${type}" role="progressbar" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100" style="width: ${percent}%">${percent}%</div></div>`;
              }
            }
            $('#mc_progress').html(html);
          }
        }
      });
    },

    get_percent(votes, total) {
      return Math.floor((votes * 100) / total) || 0;
    },

    blank_at_bottom(alternatives) {
      for (let i = 0; i < alternatives.length; i += 1) {
        if (alternatives[i] === 'Blankt') {
          alternatives.unshift(alternatives.splice(i, 1));
          return alternatives.reverse();
        }
      }
      return null;
    },
  };
}());

export default Genfors;
