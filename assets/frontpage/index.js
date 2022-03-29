import React from 'react';
import ReactDom from 'react-dom';
import { AppContainer } from 'react-hot-loader';
import EventsContainer from './events/containers/EventsContainer';
import './initFrontpage';
import './less/frontpage.less';

const renderEvents = (Events) => {
  ReactDom.render(
    <AppContainer>
      <Events />
    </AppContainer>,
    document.getElementById('event-items'),
  );
};

renderEvents(EventsContainer);

if (module.hot) {
  module.hot.accept('./events/containers/EventsContainer', () => {
    renderEvents(EventsContainer);
  });
}
