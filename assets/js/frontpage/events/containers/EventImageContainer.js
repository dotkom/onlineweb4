import React, { Component } from 'react';
import EventImage from '../components/EventImage';


class EventImageContainer extends Component {
  mergeImages() {
    const images = [];
    // Event images
    if(this.props.images.length > 0) {
      images.push(this.props.images[0]);
    }
    // Company images
    for(let company of this.props.company_event) {
      images.push(company.company.images[0]);
    }
    return images;
  }

  render() {
    return <EventImage {...this.props } images={ this.mergeImages() } />;
  }
}

export default EventImageContainer;
