import React from 'react';
import ReactDom from 'react-dom';
import { AppContainer } from 'react-hot-loader';
import Transition from 'react-transition-group/Transition';

import style from './style.less'; // eslint-disable-line no-unused-vars

const duration = 400;

const defaultStyle = {
  transition: `opacity ${duration}ms ease-in-out`,
  opacity: 0,
};

const transitionStyles = {
  entering: { opacity: 0 },
  entered: { opacity: 1 },
};

class IsLoading extends React.Component {
  constructor() {
    super();
    this.state = {
      show: false,
    };
    this.registerListeners();
  }

  registerBeforeUnloadListener() {
    window.addEventListener(
      'beforeunload',
      (event) => {
        if (this.state.show) {
          // Basic support is set by modifying the returnValue in-place rather than returning.
          // Doing both covers all bases.
          // Some browsers overrides the custom message.
          // eslint-disable-next-line no-param-reassign
          event.returnValue = 'Onlinewebben utfører en spørring som kan ta litt tid. Det er viktig at du forblir på siden under denne prosessen for å hindre tap av data.';
          return event.returnValue;
        }
        return event.returnValue;
      });
  }

  registerOW4Listeners() {
    document.addEventListener('ow4-long-xhr-start',
    () => this.setState({ show: true }));

    document.addEventListener('ow4-long-xhr-end',
    () => this.setState({ show: false }));
  }

  registerListeners() {
    this.registerOW4Listeners();
    this.registerBeforeUnloadListener();
  }

  render() {
    return (
      <Transition
        in={this.state.show}
        timeout={duration}
        appear
        mountOnEnter
        unmountOnExit
      >
        {state => (
          <div
            className="isloading__component"
            style={{
              ...defaultStyle,
              ...transitionStyles[state],
            }}
          >
            <div
              className="alert alert-info alert-dismissible"
              role="alert"
            >
              Onlinewebben gjør en spørring som kan ta litt tid.<br />
              Det er viktig at du forblir på siden under denne prosessen for å hindre tap av data.
              <button
                className="close"
                data-dismiss="alert"
              >&times;</button>
            </div>
          </div>
        )}
      </Transition>
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
