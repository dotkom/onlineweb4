import React from 'react';
import ReactDom from 'react-dom';

import IsLoading from './IsLoading';

const connect = (IsLoadingComponent) => {
  ReactDom.render(
      <IsLoadingComponent />,
    document.getElementById('isloading-component'),
  );
};

connect(IsLoading);
