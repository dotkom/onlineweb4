import React from 'react';
import ReactDom from 'react-dom';
import { AppContainer } from 'react-hot-loader';
import ArticlesContainer from './articles/containers/ArticlesContainer';
import EventsContainer from './events/containers/EventsContainer';
import './initFrontpage';
import './less/frontpage.less';

const renderArticles = (Articles) => {
  ReactDom.render(
    <AppContainer>
      <Articles />
    </AppContainer>,
    document.getElementById('article-items'),
  );
};

renderArticles(ArticlesContainer);

if (module.hot) {
  module.hot.accept('./articles/containers/ArticlesContainer', () => {
    renderArticles(ArticlesContainer);
  });
}

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
