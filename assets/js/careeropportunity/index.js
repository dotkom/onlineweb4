import React from 'react';
import ReactDom from 'react-dom';
import CareerContainer from './containers/CareerContainer';

class App extends React.Component {
  constructor() {
    super();
  }

  render() {
    return (
      <CareerContainer />
    );
  }
}

ReactDom.render(
  <App />,
  document.getElementById('career-container')
);
