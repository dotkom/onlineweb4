import React from 'react';

const MainArticle = ({ article }) => (
    <div className="col-md-6">
      <a href="{article.articleUrl}">
        <img src={article.image.sm} alt={article.heading} />
        <h3>{article.heading}</h3>
      </a>
      <p>{article.ingress}</p>
    </div>
);


export default MainArticle;
