import React, { Component } from 'react';
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

// 3 days in milliseconds
const THREE_DAYS = 3 * 24 * 60 * 60 * 1000
const DAYS_BACK_DELTA = new Date() - THREE_DAYS;
const DAYS_FORWARD_DELTA = new Date() + THREE_DAYS;

const getRegistrationFiltered = ({ attendance_event: attendance, event_start: startDate }) => {
  const registration_start = attendance !== null ? new Date(attendance.registration_start) : null;
  if (
    attendance
    && DAYS_BACK_DELTA <= registration_start
    && registration_start < DAYS_FORWARD_DELTA
  ) {
    return registration_start;
  }
  return startDate;
};

const apiEventsToEvents = event => ({
  eventUrl: `/events/${event.id}/${event.slug}`,
  ingress: event.ingress_short,
  startDate: new Date(event.event_start),
  endDate: new Date(event.event_end),
  registrationFiltered: getRegistrationFiltered(event),
  title: event.title,
  images: mergeEventImages(event.image, event.company_event),
});

const sortEvents = (a, b) => {
  // checks if the event is starting today or is ongoing
  const now = new Date();
  if (a.startDate <= now && now < a.endDate) {
    if (b.startDate <= now && now < b.endDate) {
      return a.endDate < b.endDate ? -1 : 1;
    }
    return -1;
  }
  return a.registrationFiltered < b.registrationFiltered ? -1 : 1;
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
    this.API_URL = `/api/v1/events/?event_end__gte=${new Date().toISOString().slice(0, "YYYY-MM-DD".length)}`;
    const eventTypes = [
      { id: '1', name: 'Sosialt' },
      { id: '2', name: 'Bedriftspresentasjon' },
      { id: '3', name: 'Kurs' },
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
      apiUrl += '4,5,6,7,8';
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
