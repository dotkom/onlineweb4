import loadCity from './zipcodecity';
import enableUserSearch from './userSearch';
import './profiles';
import './less/profiles.less';
import './less/typeahead.less';

loadCity();

const userSearchElement = document.getElementById('user-search');
if (userSearchElement) {
  enableUserSearch();
}
