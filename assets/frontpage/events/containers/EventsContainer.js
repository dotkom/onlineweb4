import React, { Component } from 'react';
import moment from 'moment';
import Events from '../components/Events';
import { setEventsForEventTypeId, toggleEventTypeDisplay } from '../utils';

const mergeEventImages = (eventImage, companyEvent) => {
  const eventImages = [];
  // Event images
  if (eventImage) {
    eventImages.push(eventImage);
  }
  // Company images
  const companyImages = companyEvent.map(company => (
    company.company.image
  ));
  return [...eventImages, ...companyImages];
};

const apiEventsToEvents = event => ({
  eventUrl: `/events/${event.id}/${event.slug}`,
  ingress: event.ingress_short,
  startDate: event.event_start,
  endDate: event.event_end,
  title: event.title,
  images: mergeEventImages(event.image, event.company_event),
});

const sortEvents = (a, b) => {
  // checks if the event is starting today or is ongoing
  if (moment().isBetween(a.startDate, a.endDate)) {
    if (moment().isBetween(b.startDate, b.endDate)) {
      return moment(a.endDate).isBefore(b.endDate) ? -1 : 1;
    }
    return -1;
  }
  return moment(a.startDate).isBefore(b.startDate) ? -1 : 1;
};

/*
Reduces array to object and adds some generic fields

Example:
{
  1: {
    id: '1',
    name: 'Test',
    display: true,
    ...
  },
  ...
}
*/
const initialEventTypes = eventTypes => (
  eventTypes.reduce((accumulator, eventType) => (
    Object.assign(accumulator, {
      [eventType.id]: {
        id: eventType.id,
        name: eventType.name,
        display: true,
        events: [],
        loaded: false,
      },
    })
  ), {})
);

class EventsContainer extends Component {
  constructor(props) {
    super(props);
    this.API_URL = `/api/v1/events/?event_end__gte=${moment().format('YYYY-MM-DD')}`;
    const eventTypes = [
      { id: '1', name: 'Sosialt' },
      { id: '2', name: 'Bedriftspresentasjon' },
      { id: '3', name: 'Kurs' },
      { id: '20', name: 'Sosialt' },
      { id: 'other', name: 'Annet' },
    ];
    this.state = {
      events: [],
      dirty: false,
      eventTypes: initialEventTypes(eventTypes),
    };
    this.setEventVisibility = this.setEventVisibility.bind(this);
    this.getVisibleEvents = this.getVisibleEvents.bind(this);

    this.fetchEvents();
    // Loop over event types
    Object.keys(this.state.eventTypes).forEach((eventTypeId) => {
      const eventType = this.state.eventTypes[eventTypeId];
      this.fetchEventsByType(eventType.id);
    });
  }

  getVisibleEvents() {
    const { eventTypes } = this.state;
    const allEventTypesLoaded = Object.keys(eventTypes).every(eventTypeId => (
      eventTypes[eventTypeId].loaded
    ));
    if (!allEventTypesLoaded) {
      // Show initially loaded events instead
      return this.state.events;
    }
    // Reduce all event type events to one array
    const visibleEvents = Object.keys(eventTypes).reduce((events, eventTypeId) => {
      const eventType = eventTypes[eventTypeId];
      if (eventType.display) {
        return [...events, ...eventType.events];
      }
      return events;
    }, []);

    visibleEvents.sort(sortEvents);
    return visibleEvents;
  }

  setEventVisibility(e) {
    this.setState({
      eventTypes: toggleEventTypeDisplay(this.state, e.eventType),
    });
  }

  getEventTypes() {
    const { eventTypes } = this.state;
    // Turn object into array
    return Object.keys(eventTypes).map(eventTypeId => (
      eventTypes[eventTypeId]
    ));
  }

  fetchEvents() {
    const apiUrl = `${this.API_URL}&format=json`;
    fetch(apiUrl, { credentials: 'same-origin' })
    .then(response => response.json())
    .then((json) => {
      this.setState({
        events: json.results.map(apiEventsToEvents),
      });
    });
  }

  fetchEventsByType(eventType) {
    let apiUrl = `${this.API_URL}&format=json&event_type=`;
    if (eventType === 'other') {
      apiUrl += '4,5,6,7';
    } else {
      apiUrl += eventType;
    }
    fetch(apiUrl, { credentials: 'same-origin' })
    .then(response =>
       response.json(),
    ).then((json) => {
      const events = json.results.map(apiEventsToEvents);
      this.setState({
        eventTypes: setEventsForEventTypeId(this.state, eventType, events),
      });
    });
  }

  mainEvents() {
    return this.getVisibleEvents().slice(0, 2);
  }

  smallEvents() {
    return this.getVisibleEvents().slice(2, 10);
  }

  render() {
    return (
      <Events
        mainEvents={this.mainEvents()} smallEvents={this.smallEvents()}
        setEventVisibility={this.setEventVisibility}
        eventTypes={this.getEventTypes()}
      />
    );
  }
}

export default EventsContainer;
