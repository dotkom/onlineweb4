import React, { PropTypes } from 'react';
import Event from './Event';
import SmallEvent from './SmallEvent';
import EventsHeading from './EventsHeading';

const Events = ({ mainEvents, smallEvents, setEventVisibility, eventTypes }) => (
  <div>
    <EventsHeading eventTypes={eventTypes} setEventVisibility={setEventVisibility} />
    <div className="row clearfix hero">
      {
        mainEvents.map(event =>
          <Event key={event.id} {...event} />,
        )
      }
    </div>
    <div className="row clearfix hero">
      <ul className="event-list clearfix">
        {
          smallEvents.map(event => (
            <SmallEvent key={event.id} {...event} />
          ))
        }
      </ul>
    </div>
  </div>
);

Events.propTypes = {
  eventTypes: EventsHeading.propTypes.eventTypes,
  mainEvents: PropTypes.arrayOf(PropTypes.shape(Event.propTypes)),
  setEventVisibility: EventsHeading.propTypes.setEventVisibility,
  smallEvents: PropTypes.arrayOf(PropTypes.shape(Event.propTypes)),
};

export default Events;
