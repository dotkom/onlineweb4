import React from 'react';
import ReactDom from 'react-dom';
import Events from './components/Events';

// Temporary
const events = [
  {
    date: '04. oktober',
    title: 'React event 1',
    description: 'React test',
    url: 'http://example.com'
  },
  {
    date: '05. oktober',
    title: 'React event 2',
    description: 'React test',
    url: 'http://example.com'
  }
];

ReactDom.render(
  <Events events={ events } />,
  document.getElementById('event-items')
);
