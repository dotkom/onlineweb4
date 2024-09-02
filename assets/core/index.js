import 'common/less/gallery.less';
import 'bootstrap';

import { timeOutAlerts } from 'common/utils/';
import init from './init';
import './less/core.less';

init();
timeOutAlerts();

if (import.meta.env.ENVIRONMENT === 'dev')  {
    await import('./less/staging_theme.less');
}
