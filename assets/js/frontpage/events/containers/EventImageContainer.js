import React, { Component, PropTypes } from 'react';
import EventImage from '../components/EventImage';
import CompanyPropTypes from '../proptypes/CompanyPropTypes';
import ImagePropTypes from '../proptypes/ImagePropTypes';


class EventImageContainer extends Component {
  mergeImages() {
    const { image, company_event } = this.props;
    const eventImages = [];
    // Event images
    if (image) {
      eventImages.push(image);
    }
    // Company images
    const companyImages = company_event.map(company => (
      company.company.image
    ));
    return [...eventImages, ...companyImages];
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
