import moment from 'moment';
import React from 'react';
import ReactDom from 'react-dom';
import EventsContainer from './containers/EventsContainer';
require('es6-promise').polyfill();
require('isomorphic-fetch');

moment.locale('nb');

ReactDom.render(
  <EventsContainer />,
  document.getElementById('event-items'),
);
