import React from 'react';
import PropTypes from 'prop-types';
import EventImage from '../components/EventImage';

const Event = ({ eventUrl, images, ingress, startDate, title }) => (
  <div>
    <div className="col-sm-8 col-md-4">
      <div className="hero-title">
        <a href={eventUrl}>
          <p>{ title }</p>
        </a>
      </div>
      <div className="hero-ingress hidden-xs">
        <p>{ ingress }</p>
      </div>
    </div>
    <EventImage
      date={startDate}
      images={images}
      eventUrl={eventUrl}
    />
  </div>
);

Event.propTypes = {
  eventUrl: PropTypes.string.isRequired,
  images: EventImage.propTypes.images,
  ingress: PropTypes.string.isRequired,
  startDate: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
};

export default Event;
