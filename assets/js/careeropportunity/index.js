import React from 'react';
import ReactDom from 'react-dom';
import FilterableJobList from './containers/FilterableJobList';

class App extends React.Component {
  constructor() {
    super();
  }

  render() {
    return (
      <FilterableJobList />
    );
  }
}

ReactDom.render(
  <App />,
  document.getElementById('career-container')
);
