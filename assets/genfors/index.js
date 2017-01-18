import $ from 'jquery';
import 'common/datetimepicker';
import Genfors from './Genfors';
import registeredVoters from './registeredVoters';
import './less/genfors.less';

const genforsElement = document.getElementById('generalforsamling-question');
if (genforsElement) {
  Genfors.vote.bind_buttons();
  setInterval(Genfors.update, 10000);
}

const voteButton = document.querySelector('.vote-button');
if (voteButton) {
  registeredVoters();
}

const yesterday = () => {
  const date = new Date();
  date.setDate(date.getDate() - 1); // Yesterday
  return date;
};

// Check for existence of input fields that require bootstrap datetimepicker
// And activate it on these objects.
$('#id_start_date').datetimepicker({
  locale: 'nb',
  format: 'YYYY-MM-DD',
  minDate: yesterday(),
});
