import React, { PropTypes } from 'react';
import Event from './Event';
import SmallEvent from './SmallEvent';
import EventsHeading from './EventsHeading';

const Events = ({ mainEvents, smallEvents, filterEvents, eventTypes }) => (
  <div>
    <EventsHeading eventTypes={ eventTypes } filterEvents={ filterEvents } />
    <div className="row clearfix hero">
    {
      mainEvents.map((event) => {
        return <Event { ...event } />
      }) 
    }
    </div>
    <div className="row clearfix hero">
      <ul className='event-list clearfix'>
        {
          smallEvents.map((event) => (
            <SmallEvent { ...event } />
          ))
        }
      </ul>
    </div>
  </div>
);

Events.propTypes = {
  events: PropTypes.arrayOf(PropTypes.shape(Event.propTypes))
};

export default Events;
