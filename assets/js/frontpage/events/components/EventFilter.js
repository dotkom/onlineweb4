import React, { PropTypes } from 'react';
import { ButtonGroup, Button } from 'react-bootstrap';

const EventFilter = ({ eventTypes, setEventVisibility }) => (
  <ButtonGroup className="event-filters">
    { eventTypes.map((eventType, index) => (
      <Button
        key={index} bsSize="xsmall"
        className={eventType.display ? `event-${eventType.name.toLowerCase()}` : 'hidden-event-button'}
        onClick={() => setEventVisibility({ eventType })}
      >
        { eventType.name }
      </Button>
    ))
    }
  </ButtonGroup>
);


EventFilter.propTypes = {
  eventTypes: PropTypes.arrayOf(PropTypes.shape({
    display: PropTypes.bool.isRequired,
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
  })).isRequired,
  setEventVisibility: PropTypes.func.isRequired,
};


export default EventFilter;
