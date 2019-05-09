import PropTypes from 'prop-types';

import ImagePropTypes from 'common/proptypes/ImagePropTypes';

const ResourcePropTypes = PropTypes.shape({
  image: ImagePropTypes,
  id: PropTypes.number,
  title: PropTypes.string,
  priority: PropTypes.number,
  description: PropTypes.string,
});

export default ResourcePropTypes;
