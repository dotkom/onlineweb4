import React, { Component } from 'react';
import Events from '../components/Events';

class EventsContainer extends Component {
  constructor(props) {
    super(props);
    this.API_URL = `/api/v1/events/?event_end__gte=${moment().format('YYYY-MM-DD')}&format=json`;
    this.state = {
      events: [],
      visibleEvents: []  
    };
    this.showKurs = true; 
    this.showBedpress = true; 
    this.showSocial = true; 
    this.showOther = true;
    this.fetchEvents();
  }

  fetchEvents() {
    fetch(this.API_URL)
    .then(response => {
      return response.json();
    }).then(json => {
      this.setState({
        events: json.results,
        visibleEvents: json.results
      });
    }).catch(e => {
      console.error('Failed to fetch events:', e);
    });
  }
  
  setEventVisibility(e) {
    const self = this;

    switch(e.eventType.id) {
      case 2:
        self.showBedpress = !self.showBedpress;
        break;
      case 3:
        self.showKurs = !self.showKurs;
        break;
      case 1: 
        self.showSocial = !self.showSocial;
        break;
      case 4:
        self.showOther = !self.showOther;
    }

    const newEvents = this.state.events.filter(function (event) {
      if(event.event_type === 1){
        return self.showSocial;
      } else if(event.event_type === 2){
        return self.showBedpress;
      } else if(event.event_type === 3){
        return self.showKurs;
      } else if(event.event_type > 3){
        return self.showOther;
      }
    });

    this.setState({
      visibleEvents: newEvents
    });
  }

  mainEvents() {
    return this.state.visibleEvents.slice(0,2);
  }

  smallEvents() {
    return this.state.visibleEvents.slice(2, 10);
  }

  render() {
    const eventTypes = [
      {id: 1, name: 'Sosialt', display: this.showSocial},
      {id: 2, name: 'Bedriftspresentasjon', display: this.showBedpress},
      {id: 3, name: 'Kurs', display: this.showKurs},
      {id: 4, name: 'Annet', display: this.showOther}
    ];
    console.log('rerendering events')
    return (
      <Events mainEvents={ this.mainEvents() } smallEvents={ this.smallEvents() } setEventVisibility={ this.setEventVisibility.bind(this) } eventTypes={ this.eventTypes } />
    )
  }
}

export default EventsContainer;
