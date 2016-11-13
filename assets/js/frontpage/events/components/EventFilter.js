import React, { PropTypes } from 'react';
import { ButtonGroup, Button } from 'react-bootstrap';
import classNames from 'classnames';

const EventFilter = ({ eventTypes, setEventVisibility }) => (
  <ButtonGroup className="event-filters">
    { eventTypes.map((eventType, index) => {
      const filterButtonClass = classNames('event-filter-button', {
        'hidden-event-button': !eventType.display,
      });
      return (<Button
        key={index} bsSize="xsmall"
        className={filterButtonClass}
        onClick={() => setEventVisibility({ eventType })}
      >
        { eventType.name }
      </Button>);
    })
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
