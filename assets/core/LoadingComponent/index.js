import React from 'react';
import ReactDom from 'react-dom';
import { AppContainer } from 'react-hot-loader';

import IsLoading from './IsLoading';

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
  module.hot.accept('./IsLoading', () => {
    connect(IsLoading);
  });
}
