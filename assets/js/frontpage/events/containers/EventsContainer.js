import React, { Component } from 'react';
import Events from '../components/Events';

class EventsContainer extends Component {
  constructor(props) {
    super(props);

    this.API_URL = 'https://online.ntnu.no/api/v1/events/?event_end__gte=2016-10-05&format=json';
    this.state = {
      events: []
    };
    this.fetchEvents();
  }

  fetchEvents() {
    fetch(this.API_URL, {
      method: 'GET'
    }).then(function(response) {
      return response.json().then(function(json) {
        return json;
      })
    }).then(function(json) {
      this.setState({
        events: json.results
      });
    }.bind(this));
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
