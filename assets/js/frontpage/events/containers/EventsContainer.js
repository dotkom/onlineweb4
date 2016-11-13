import React, { Component } from 'react';
import moment from 'moment';
import Events from '../components/Events';

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
  title: event.title,
  images: mergeEventImages(event.image, event.company_event),
});

const sortEvents = (a, b) => {
  // checks if the event is starting today or ongoing
  if (moment().isAfter(a.event_start, 'day') && moment().isBefore(a.event_end)) {
    return 1;
  }
  // checks which event comes first
  if (moment(a.event_start).isBefore(b.event_start)) {
    return 1;
  }
  return -1;
};

class EventsContainer extends Component {
  constructor(props) {
    super(props);
    this.API_URL = `/api/v1/events/?event_end__gte=${moment().format('YYYY-MM-DD')}`;
    this.state = {
      events: [],
      eventTypes: {
        1: { id: 1, name: 'Sosialt', display: true, events: [] },
        2: { id: 2, name: 'Bedriftspresentasjon', display: true, events: [] },
        3: { id: 3, name: 'Kurs', display: true, events: [] },
        4: { id: 4, name: 'Annet', display: true, events: [] },
      },
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
    const eventTypeId = e.eventType.id;
    this.setState({
      eventTypes: Object.assign({}, this.state.eventTypes, {
        [eventTypeId]: Object.assign({}, e.eventType, {
          display: !e.eventType.display,
        }),
      }),
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
    fetch(apiUrl)
    .then(response => response.json())
    .then((json) => {
      this.setState({
        events: json.results.map(apiEventsToEvents),
      });
    });
  }

  fetchEventsByType(eventType) {
    const apiUrl = `${this.API_URL}&event_type=${eventType}&format=json`;
    fetch(apiUrl)
    .then(response =>
       response.json(),
    ).then((json) => {
      const events = json.results.map(apiEventsToEvents);
      this.setState({
        eventTypes: Object.assign({}, this.state.eventTypes, {
          [eventType]: Object.assign({}, this.state.eventTypes[eventType], {
            events,
          }),
        }),
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
