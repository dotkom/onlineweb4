import React from 'react';
import ReactDom from 'react-dom';
import { AppContainer } from 'react-hot-loader';

import style from './style.less'; // eslint-disable-line no-unused-vars

class IsLoading extends React.Component {
  constructor() {
    super();
    this.state = {
      show: false,
    };
    this.registerListeners();
  }

  registerListeners() {
    document.addEventListener('ow4-long-xhr-start',
    () => this.setState({ show: true }));

    document.addEventListener('ow4-long-xhr-end',
    () => this.setState({ show: false }));
  }

  render() {
    return (
      <div className="isloading__component">
        {this.state.show && <div
          className="alert alert-info"
        >
          Onlinewebben gjør en spørring som kan ta litt tid.<br />
          Det er viktig at du forblir på siden under denne prosessen for å hindre tap av data.
        </div>}
      </div>
    );
  }
}


const connect = (IsLoadingComponent) => {
  ReactDom.render(
    <AppContainer>
      <IsLoadingComponent />
    </AppContainer>,
    document.getElementById('isloading-component'),
  );
};

connect(IsLoading);

if (module.hot) {
  module.hot.accept('./index.js', () => {
    connect(IsLoading);
  });
}


export default IsLoading;
