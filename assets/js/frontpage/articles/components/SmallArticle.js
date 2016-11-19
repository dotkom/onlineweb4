import React, { PropTypes } from 'react';
import ImagePropTypes from 'common/proptypes/ImagePropTypes';

const SmallArticle = ({ articleUrl, heading, image }) => (
  <div className="col-xs-6 col-md-2">
    <a href={articleUrl}>
      <img src={image.thumb} alt={heading} />
      <br />
      <h4>{heading}</h4>
    </a>
  </div>
);

SmallArticle.propTypes = {
  articleUrl: PropTypes.string.isRequired,
  heading: PropTypes.string.isRequired,
  image: ImagePropTypes.isRequired,
};


export default SmallArticle;
