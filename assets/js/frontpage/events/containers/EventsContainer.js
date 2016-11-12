import React, { Component } from 'react';
import moment from 'moment';
import Events from '../components/Events';

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
    this.fetchEvents();
    this.visibleEvents = this.state.events;
    this.eventTypes = [
      { id: 1, name: 'Sosialt', display: this.state.showSocial },
      { id: 2, name: 'Bedriftspresentasjon', display: this.state.showBedpress },
      { id: 3, name: 'Kurs', display: this.state.showKurs },
      { id: 4, name: 'Annet', display: this.state.showOther },
    ];
    this.fetchEventsByType(1);
    this.fetchEventsByType(2);
    this.fetchEventsByType(3);
    this.fetchEventsByType(4);
  }

  fetchEvents() {
    const apiUrl = `${this.API_URL}&format=json`;
    fetch(apiUrl)
    .then(response =>
       response.json(),
    ).then((json) => {
      this.visibleEvents = json.results;
      this.setState({
        events: json.results,
      });
    }).catch((e) => {
      console.error('Failed to fetch events:', e);
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
        this.state.socialEvents = json.results;
      } else if (eventType === 2) {
        this.state.bedpressEvents = json.results;
      } else if (eventType === 3) {
        this.state.kursEvents = json.results;
      } else if (eventType > 3) {
        this.state.otherEvents = json.results;
      }
    }).catch((e) => {
      console.error('Failed to fetch events by type:', e);
    });
  }

  setEventVisibility(e) {
    const self = this;
    switch (e.eventType.id) {
      case 2:
        self.setState({
          showBedpress: !self.state.showBedpress,
        });
        break;
      case 3:
        self.setState({
          showKurs: !self.state.showKurs,
        });
        break;
      case 1:
        self.setState({
          showSocial: !self.state.showSocial,
        });
        break;
      case 4:
        self.setState({
          showOther: !self.state.showOther,
        });
    }
  }

  getVisibleEvents() {
    const self = this;
    let visibleEvents = [];
    if (self.state.showSocial) {
      visibleEvents = visibleEvents.concat(this.state.socialEvents);
    }
    if (self.state.showBedpress) {
      visibleEvents = visibleEvents.concat(this.state.bedpressEvents);
    }
    if (self.state.showKurs) {
      visibleEvents = visibleEvents.concat(this.state.kursEvents);
    }
    if (self.state.showOther) {
      visibleEvents = visibleEvents.concat(this.state.otherEvents);
    }
    this.sortEvents(visibleEvents);
    this.visibleEvents = visibleEvents;
  }

  mainEvents() {
    return this.visibleEvents.slice(0, 2);
  }

  smallEvents() {
    return this.visibleEvents.slice(2, 10);
  }

  sortEvents(events) {
    events.sort((a, b) =>
       (
        // checks if the event is starting today or ongoing
        (moment().isAfter(a.event_start, 'day') && moment().isBefore(a.event_end)) ? 1 :
        // checks which event comes first
        moment(a.event_start).isBefore(b.event_start) ? 1 : -1),
    );
  }

  render() {
    this.getVisibleEvents();
    return (
      <Events mainEvents={this.mainEvents()} smallEvents={this.smallEvents()} setEventVisibility={this.setEventVisibility.bind(this)} eventTypes={this.eventTypes} />
    );
  }
}

export default EventsContainer;
