import Filters from './filters';
import './less/event_archive.less';

const filters = new Filters();
filters.bindEventListeners();
filters.search();
