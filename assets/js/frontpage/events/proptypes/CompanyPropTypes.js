import { PropTypes } from 'react';
import ImagePropTypes from './ImagePropTypes';

export default {
  name: PropTypes.string,
  site: PropTypes.string,
  image: PropTypes.shape(ImagePropTypes),
};
