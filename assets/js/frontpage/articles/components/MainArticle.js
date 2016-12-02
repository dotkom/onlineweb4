import React, { PropTypes } from 'react';
import ImagePropTypes from 'common/proptypes/ImagePropTypes';

const MainArticle = ({ articleUrl, heading, image, ingress }) => (
  <div className="col-md-6">
    <a href={articleUrl}>
      <img src={image.sm} alt={heading} />
      <h3>{heading}</h3>
    </a>
    <p>{ingress}</p>
  </div>
);

MainArticle.propTypes = {
  articleUrl: PropTypes.string.isRequired,
  heading: PropTypes.string.isRequired,
  image: ImagePropTypes.isRequired,
  ingress: PropTypes.string.isRequired,
};

export default MainArticle;
