import React from 'react';
import ReactDom from 'react-dom';
import moment from 'moment';
import FilterableJobList from './containers/FilterableJobList';

require('es6-promise').polyfill();

moment.locale('nb');

ReactDom.render(
  <FilterableJobList />,
  document.getElementById('career'),
);
