import React from 'react';
import ReactDom from 'react-dom';
import EventsContainer from './containers/EventsContainer';

ReactDom.render(
  <EventsContainer />,
  document.getElementById('event-items'),
);
