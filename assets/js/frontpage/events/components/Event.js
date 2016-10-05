import React, { PropTypes } from 'react';
import EventImage from './EventImage';

const Event = ({ event_start, id, images, ingress_short, slug, title }) => (
  <div>
    <div className="col-sm-8 col-md-4">
      <div className="hero-title">
        <a href={ `events/${id}/${slug}` }>
          <p>{ title }</p>
        </a>
      </div>
      <div className="hero-ingress hidden-xs">
        <p>{ ingress_short }</p>
      </div>
    </div>
    <EventImage event_start= {event_start } images={ images } />
  </div>
);

Event.propTypes = {
  date: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  url: PropTypes.string.isRequired
};

export default Event;
