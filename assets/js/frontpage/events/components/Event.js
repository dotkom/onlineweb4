import React, { PropTypes } from 'react';
import EventImageContainer from '../containers/EventImageContainer';

const Event = ({ company_event, event_start, id, image, ingress_short, slug, title }) => (
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
    <EventImageContainer
      company_event={ company_event }
      event_start= {event_start }
      id={ id }
      image={ image }
      slug={ slug }
    />
  </div>
);

Event.propTypes = {
  description: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired
};

export default Event;
