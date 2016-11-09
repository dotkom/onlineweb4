import React, { PropTypes } from 'react';
import Event from './Event';
import SmallEvent from './SmallEvent';
import EventsHeading from './EventsHeading';

const Events = ({ mainEvents, smallEvents, setEventVisibility, eventTypes }) => (
  <div>
    <EventsHeading eventTypes={ eventTypes } setEventVisibility={ setEventVisibility } />
    <div className="row clearfix hero">
      {
        mainEvents.map((event) => {
          return <Event key={ event.id } { ...event } />
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
