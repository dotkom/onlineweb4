import React from 'react';
import { ButtonGroup, Button } from 'react-bootstrap';

const EventFilter = ({ eventTypes, filterEvents }) => (
  <ButtonGroup className="event-filters">
    { eventTypes.map((eventType) => (
        <Button bsSize="xsmall" bsStyle={ eventType[2] ? 'primary' : 'default'} onClick={ () => filterEvents({ eventType }) }> { eventType[1] } </Button>
      ))
    }
  </ButtonGroup>
);

export default EventFilter;
