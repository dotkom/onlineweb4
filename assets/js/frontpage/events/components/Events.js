import React, { PropTypes } from 'react';
import Event from './Event';

const Events = ({ events }) => (
  <div id="event-items">
    <div className="row clearfix hero">
    {
      events.map((event) => {
        return <Event { ...event } />
      })
    }
    </div>
  </div>
);

Events.propTypes = {
  events: PropTypes.arrayOf(PropTypes.shape(Event.propTypes))
};

export default Events;
