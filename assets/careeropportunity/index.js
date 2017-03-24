import React from 'react';
import ReactDom from 'react-dom';
import FilterableJobList from './containers/FilterableJobList';

require('es6-promise').polyfill();
require('isomorphic-fetch');

ReactDom.render(
  <FilterableJobList />,
  document.getElementById('career'),
);
