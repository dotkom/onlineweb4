import React from 'react';
import ReactDom from 'react-dom';
import ArticlesContainer from './containers/ArticlesContainer';

require('es6-promise').polyfill();
require('isomorphic-fetch');

ReactDom.render(
  <ArticlesContainer />,
  document.getElementById('article-items'),
);
