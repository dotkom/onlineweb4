import React from 'react';
import ReactDom from 'react-dom';
import ArticlesContainer from './containers/ArticlesContainer';

ReactDom.render(
  <ArticlesContainer />,
  document.getElementById('article-items'),
);
