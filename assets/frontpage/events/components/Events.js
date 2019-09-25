import React from 'react';
import PropTypes from 'prop-types';
import Event from './Event';
import SmallEvent from './SmallEvent';
import EventsHeading from './EventsHeading';

const Events = ({ mainEvents, smallEvents, setEventVisibility, eventTypes }) => (
  <div>
    <EventsHeading eventTypes={eventTypes} setEventVisibility={setEventVisibility} />
    <div className="row clearfix hero">
      {
        mainEvents.length !== 0
        ? mainEvents.map((event, index) =>
          <Event key={index} {...event} />,
        )
        : <div className="col-lg-12">Ingen arrangementer funnet, eller de er blokert av en adblock.</div>
      }
    </div>
    <div className="row clearfix hero">
      <ul className="event-list clearfix">
        {
          smallEvents.map((event, index) => (
            <SmallEvent key={index} {...event} />
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
