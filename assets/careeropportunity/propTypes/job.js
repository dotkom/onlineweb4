import PropTypes from 'prop-types';
import companyImageProps from './companyImage';

export default {
  locations: PropTypes.arrayOf(PropTypes.string),
  deadline: PropTypes.string,
  companyImage: companyImageProps,
  companyName: PropTypes.string,
  applicationLink: PropTypes.string,
  title: PropTypes.string,
  ingress: PropTypes.string,
  type: PropTypes.string,
  id: PropTypes.number,
};
