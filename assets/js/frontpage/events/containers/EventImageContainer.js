import React, { Component, PropTypes } from 'react';
import EventImage from '../components/EventImage';
import CompanyPropTypes from '../proptypes/CompanyPropTypes';
import ImagePropTypes from '../proptypes/ImagePropTypes';


class EventImageContainer extends Component {
  mergeImages() {
    const images = [];
    // Event images
    if (this.props.image) {
      images.push(this.props.image);
    }
    // Company images
    for (const company of this.props.company_event) {
      images.push(company.company.image);
    }
    return images;
  }

  render() {
    return <EventImage {...this.props} images={this.mergeImages()} />;
  }
}

EventImageContainer.propTypes = {
  company_event: PropTypes.arrayOf(PropTypes.shape({
    company: PropTypes.shape(CompanyPropTypes),
    event: PropTypes.number,
  })),
  image: PropTypes.shape(ImagePropTypes),
};

export default EventImageContainer;
