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
      showKurs: true,
      showBedpress: true,
      showSocial: true,
      showOther: true,
      socialEvents: [],
      bedpressEvents: [],
      kursEvents: [],
      otherEvents: [],
    };
    this.setEventVisibility = this.setEventVisibility.bind(this);
    this.getVisibleEvents = this.getVisibleEvents.bind(this);
    this.fetchEvents();
    this.eventTypes = [
      { id: 1, name: 'Sosialt', display: this.state.showSocial },
      { id: 2, name: 'Bedriftspresentasjon', display: this.state.showBedpress },
      { id: 3, name: 'Kurs', display: this.state.showKurs },
      { id: 4, name: 'Annet', display: this.state.showOther },
    ];
    this.eventTypes.forEach((eventType) => {
      this.fetchEventsByType(eventType.id);
    });
  }

  getVisibleEvents() {
    let visibleEvents = [];
    if (this.state.showSocial) {
      visibleEvents = visibleEvents.concat(this.state.socialEvents);
    }
    if (this.state.showBedpress) {
      visibleEvents = visibleEvents.concat(this.state.bedpressEvents);
    }
    if (this.state.showKurs) {
      visibleEvents = visibleEvents.concat(this.state.kursEvents);
    }
    if (this.state.showOther) {
      visibleEvents = visibleEvents.concat(this.state.otherEvents);
    }
    visibleEvents.sort(sortEvents);
    return visibleEvents;
  }

  setEventVisibility(e) {
    switch (e.eventType.id) {
      case 2:
        this.setState({
          showBedpress: !this.state.showBedpress,
        });
        break;
      case 3:
        this.setState({
          showKurs: !this.state.showKurs,
        });
        break;
      case 1:
        this.setState({
          showSocial: !this.state.showSocial,
        });
        break;
      case 4:
        this.setState({
          showOther: !this.state.showOther,
        });
        break;
      default:
        break;
    }
  }

  fetchEvents() {
    const apiUrl = `${this.API_URL}&format=json`;
    fetch(apiUrl)
    .then(response =>
       response.json(),
    ).then((json) => {
      this.visibleEvents = json.results;
      this.setState({
        events: json.results.map(apiEventsToEvents),
      });
    });
  }

  fetchEventsByType(eventType) {
    // problem: other, flere eventtyper
    const apiUrl = `${this.API_URL}&event_type=${eventType}&format=json`;
    fetch(apiUrl)
    .then(response =>
       response.json(),
    ).then((json) => {
      if (eventType === 1) {
        this.state.socialEvents = json.results.map(apiEventsToEvents);
      } else if (eventType === 2) {
        this.state.bedpressEvents = json.results.map(apiEventsToEvents);
      } else if (eventType === 3) {
        this.state.kursEvents = json.results.map(apiEventsToEvents);
      } else if (eventType > 3) {
        this.state.otherEvents = json.results.map(apiEventsToEvents);
      }
    }).catch((e) => {
      console.error('Failed to fetch events by type:', e);
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
        eventTypes={this.eventTypes}
      />
    );
  }
}

export default EventsContainer;
