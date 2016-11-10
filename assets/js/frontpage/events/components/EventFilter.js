import React from 'react';
import { ButtonGroup, Button } from 'react-bootstrap';

const EventFilter = ({ eventTypes, setEventVisibility }) => (
  <ButtonGroup className="event-filters">
    { eventTypes.map((eventType, index) => (
      <Button key={index} bsSize="xsmall" className={eventType.display ? `event-${eventType.name.toLowerCase()}` : 'hidden-event-button'} onClick={() => setEventVisibility({ eventType })}> { eventType.name } </Button>
      ))
    }
  </ButtonGroup>
);

export default EventFilter;
