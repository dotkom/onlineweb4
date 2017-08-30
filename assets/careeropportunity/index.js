import React from 'react';
import ReactDom from 'react-dom';
import moment from 'moment';
import FilterableJobList from './containers/FilterableJobList';
import DetailView from './containers/DetailView';
import { Router, Route, Switch, Link, IndexRoute, hashHistory } from 'react-router';

import createBrowserHistory from 'history/createBrowserHistory'

require('es6-promise').polyfill();
require('isomorphic-fetch');

moment.locale('nb');

const history = createBrowserHistory();
const App = () => {
  return (
    <Router history={history}>
      <Switch>
        <Route exact path='/careeropportunity/' component={FilterableJobList} />
        <Route path='/careeropportunity/:id' component={DetailView} />
      </Switch>

    </Router>
  );
}

ReactDom.render(
  <App />,
  document.getElementById('career'),
);
