import Genfors from './Genfors';
import './less/genfors.less';

Genfors.vote.bind_buttons();
setInterval(Genfors.update, 10000);
