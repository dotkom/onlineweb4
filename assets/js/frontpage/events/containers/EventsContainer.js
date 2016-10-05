import React, { Component } from 'react';
import Events from '../components/Events';

class EventsContainer extends Component {
  constructor(props) {
    super(props);

    this.API_URL = 'https://online.ntnu.no/api/v1/events/?format=json';
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

  render() {
    return (
      <Events events={ this.state.events } />
    )
  }
}

export default EventsContainer;
