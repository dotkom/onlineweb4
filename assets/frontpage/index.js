import React from 'react';
import ReactDom from 'react-dom';
import ArticlesContainer from './articles/containers/ArticlesContainer';
import Business from './business/components/Business';
import EventsContainer from './events/containers/EventsContainer';
import './initFrontpage';

ReactDom.render(
  <ArticlesContainer />,
  document.getElementById('article-items'),
);

ReactDom.render(
  <EventsContainer />,
  document.getElementById('event-items'),
);

ReactDom.render(
	<Business />,
	document.getElementById('business-items'),
);