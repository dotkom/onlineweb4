import React from 'react';
import ReactDom from 'react-dom';
import moment from 'moment';
import App from './containers/App';
import './less/career.less';

require('es6-promise').polyfill();
require('isomorphic-fetch');

moment.locale('nb');


ReactDom.render(
  <App />,
  document.getElementById('career'),
);
