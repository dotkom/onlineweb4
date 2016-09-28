import React from 'react';
import ReactDom from 'react-dom';
import Header from './components/Header';
import Events from './components/Events';

const App = () => (
  <div className="container">
      <Header />
      <Events />
  </div>
);

ReactDom.render(
  <App />,
  document.getElementById('events')
);
