import React from 'react';
import ReactDom from 'react-dom';
import Header from './components/Header';
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

const App = () => (
  <div className="container">
      <Header />
      <Events events={ events } />
  </div>
);

ReactDom.render(
  <App />,
  document.getElementById('events')
);
