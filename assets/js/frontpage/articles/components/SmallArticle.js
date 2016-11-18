import React from 'react';

const SmallArticle = ({ article }) => (
    <div className="col-xs-6 col-md-2">
      <a href={article.articleUrl}>
        <img src={article.image.thumb} alt={article.heading} />
        <br />
        <h4>{article.heading}</h4>
      </a>
    </div>
);


export default SmallArticle;
