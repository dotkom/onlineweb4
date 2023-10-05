import React from 'react';
import ReactDom from 'react-dom';
import moment from 'moment';
import App from './containers/App';
import './less/career.less';

moment.locale('nb');


ReactDom.render(
  <App />,
  document.getElementById('career'),
);
