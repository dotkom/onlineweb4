import 'common/less/gallery.less';
import moment from 'moment';
import 'bootstrap';
// Polyfills
import 'es6-promise/auto';
import 'whatwg-fetch';
import 'picturefill';

import { timeOutAlerts } from 'common/utils/';
import { initGoogleMaps } from './maps';
import init from './init';
import './less/core.less';


moment.locale('nb');

initGoogleMaps();
init();
timeOutAlerts();
