import React from 'react';
import { BrowserRouter as ReactRouter, Switch, Route } from 'react-router-dom';
import Urls from 'urls';

import HobbiessList from './containers/HobbiesList';
import NewHobby from './containers/NewHobby';
import EditHobby from './containers/EditHobby';

const Router = () => {
  const basePath = Urls.hobbies_dashboard_index();
  return (
    <ReactRouter>
      <Switch>
        <Route exact path={`${basePath}`} component={HobbiessList} />
        <Route path={`${basePath}new`} component={NewHobby} />
        <Route path={`${basePath}edit/:id`} render={({ match }) => <EditHobby id={match.params.id} />} />
      </Switch>
    </ReactRouter>
  );
};

export default Router;
