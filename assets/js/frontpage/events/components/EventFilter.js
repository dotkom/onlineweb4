import React from 'react';
import { ButtonGroup, Button } from 'react-bootstrap';

const EventFilter = ({ eventTypes, filterEvents }) => (
  <ButtonGroup>
    { eventTypes.map((eventType) => (
        <Button bsStyle={ eventType[2] ? 'primary' : ''} onClick={ () => filterEvents({ eventType }) }> { eventType[1] } </Button>
      ))
    }
  </ButtonGroup>
);

export default EventFilter;
