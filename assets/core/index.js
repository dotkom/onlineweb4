import 'common/less/gallery.less';
import moment from 'moment';
// Polyfills
import 'es6-promise/auto';
import 'whatwg-fetch';
import 'picturefill';

import { timeOutAlerts } from 'common/utils/';
import { initGoogleMaps, initialize } from './init.js';
import './less/core.less';


moment.locale('nb');

initGoogleMaps();
initialize();
timeOutAlerts();
