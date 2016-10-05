import React, { Component } from 'react';
import Events from '../components/Events';

class EventsContainer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      events: [
        {
          date: '04. oktober',
          title: 'React event 1',
          description: 'React test',
          url: 'http://example.com'
        },
        {
          date: '05. oktober',
          title: 'React event 2',
          description: 'React test',
          url: 'http://example.com'
        }
      ]
    };
  }

  render() {
    return (
      <Events events={ this.state.events } />
    )
  }
}

export default EventsContainer;
