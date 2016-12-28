import $ from 'jquery';
import cityFromZipCode from './zipcodecity';
import enableUserSearch from './userSearch';
import './profiles';
import './less/profiles.less';
import './less/typeahead.less';

const zipCode = $('#zip-code').text();
cityFromZipCode(zipCode).then((city) => {
  $('#city').html(`&nbsp;${city}`);
});

const userSearchElement = document.getElementById('user-search');
if (userSearchElement) {
  enableUserSearch();
}
