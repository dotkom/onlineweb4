import React, { PropTypes } from 'react';
import EventImage from './EventImage';

const Event = ({ date, description, title, url }) => (
  <div>
    <div className="col-sm-8 col-md-4">
      <div className="hero-title">
        <a href={ url }>
          <p>{ title }</p>
        </a>
      </div>
      <div className="hero-ingress hidden-xs">
        <p>{ description }</p>
      </div>
    </div>
    <EventImage date={ date } />
  </div>
);

Event.propTypes = {
  date: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  url: PropTypes.string.isRequired
};

export default Event;
