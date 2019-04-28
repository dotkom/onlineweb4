import PropTypes from 'prop-types';

export default PropTypes.objectOf(PropTypes.shape({
  id: PropTypes.number,
  name: PropTypes.string,
  display: PropTypes.bool,
  deadline: PropTypes.number,
}));
