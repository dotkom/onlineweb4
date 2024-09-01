import React from 'react';
import ReactDom from 'react-dom';
import ArticlesContainer from './articles/containers/ArticlesContainer';
import './less/frontpage.less';

const renderArticles = (Articles) => {
  ReactDom.render(
      <Articles />,
    document.getElementById('article-items'),
  );
};

renderArticles(ArticlesContainer);
