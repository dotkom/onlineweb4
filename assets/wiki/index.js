import { prettyPrintCode } from './utils';
import './less/wiki.less';

prettyPrintCode();

// Quick fix for dropdown toggles
window.$('.dropdown-toggle').dropdown();
