import React from 'react';
import { BrowserRouter as ReactRouter, Switch, Route } from 'react-router-dom';
import Urls from 'urls';

import ResourcesList from './containers/ResourcesList';
import NewResource from './containers/NewResource';
import EditResource from './containers/EditResource';

const Router = () => {
  const basePath = Urls.resources_dashboard_index();
  return (
    <ReactRouter>
      <Switch>
        <Route exact path={`${basePath}`} component={ResourcesList} />
        <Route path={`${basePath}new`} component={NewResource} />
        <Route path={`${basePath}edit/:id`} render={({ match }) => <EditResource id={match.params.id} />} />
      </Switch>
    </ReactRouter>
  );
};

export default Router;
