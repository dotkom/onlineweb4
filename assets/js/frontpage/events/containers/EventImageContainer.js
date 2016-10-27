import React, { Component } from 'react';
import EventImage from '../components/EventImage';


class EventImageContainer extends Component {
  mergeImages() {
    const images = [];
    // Event images
    if(this.props.image) {
      images.push(this.props.image.lg);
    }
    // Company images
    for(let company of this.props.company_event) {
      images.push(company.company.image.lg);
    }
    return images;
  }

  render() {
    return <EventImage {...this.props } images={ this.mergeImages() } />;
  }
}

export default EventImageContainer;
