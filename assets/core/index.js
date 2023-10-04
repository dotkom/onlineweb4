import 'common/less/gallery.less';
import moment from 'moment';
import 'bootstrap';

import { timeOutAlerts } from 'common/utils/';
import init from './init';
import './less/core.less';


moment.locale('nb');

init();
timeOutAlerts();
