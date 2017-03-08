import React, { PropTypes } from 'react';
import ArticlesHeading from './ArticlesHeading';
import MainArticle from './MainArticle';
import SmallArticle from './SmallArticle';

const Articles = ({ mainArticles, smallArticles }) => (
  <div>
    <ArticlesHeading />
    <div className="row row-space">
      {
        mainArticles.map((article, index) => (
          <MainArticle {...article} key={index} />
        ))
      }
      {
        smallArticles.map((article, index) => (
          <SmallArticle {...article} key={index} />
        ))
      }
    </div>
  </div>
);

Articles.propTypes = {
  mainArticles: PropTypes.arrayOf(PropTypes.shape(MainArticle.propTypes)),
  smallArticles: PropTypes.arrayOf(PropTypes.shape(SmallArticle.propTypes)),
};


export default Articles;
