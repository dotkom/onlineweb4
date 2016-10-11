import React, { Component } from 'react';
import Events from '../components/Events';

class EventsContainer extends Component {
  constructor(props) {
    super(props);
    this.API_URL = `/api/v1/events/?event_end__gte=${moment().format('YYYY-MM-DD')}&format=json`;
    this.state = {
      events: []
    };
    this.fetchEvents();
  }

  fetchEvents() {
    fetch(this.API_URL)
    .then(response => {
      return response.json();
    }).then(json => {
      this.setState({
        events: json.results
      });
    }).catch(e => {
      console.error('Failed to fetch events:', e);
    });
  }

  mainEvents() {
    return this.state.events.slice(0,2);
  }

  smallEvents() {
    return this.state.events.slice(2)
  }

  render() {
    return (
      <Events mainEvents={ this.mainEvents() } smallEvents={ this.smallEvents() } />
    )
  }
}

export default EventsContainer;
