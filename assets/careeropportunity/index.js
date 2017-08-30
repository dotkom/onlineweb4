import React from 'react';
import ReactDom from 'react-dom';
import moment from 'moment';
import FilterableJobList from './containers/FilterableJobList';
//import DetailView from './containers/DetailView';
import { Router, Route, Link, IndexRoute, hashHistory, browserHistory } from 'react-router';

require('es6-promise').polyfill();
require('isomorphic-fetch');

moment.locale('nb');

const routes = (
  <Route history={browserHistory}>
    <Route path='/careeropportunity' component={FilterableJobList} />
    <Route path='/careeropportunity/*' component={FilterableJobList} />
  </Route>
);

ReactDom.render(
  <FilterableJobList />,
  document.getElementById('career'),
);
