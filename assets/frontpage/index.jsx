import React from 'react';
import ReactDom from 'react-dom';
import ArticlesContainer from './articles/containers/ArticlesContainer';
import EventsContainer from './events/containers/EventsContainer';
import './initFrontpage';
import './less/frontpage.less';

const renderArticles = (Articles) => {
  ReactDom.render(
      <Articles />,
    document.getElementById('article-items'),
  );
};

renderArticles(ArticlesContainer);

const renderEvents = (Events) => {
  ReactDom.render(
      <Events />,
    document.getElementById('event-items'),
  );
};

renderEvents(EventsContainer);
