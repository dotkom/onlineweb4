import React from 'react';
import { Glyphicon } from 'react-bootstrap';
import Urls from 'urls';
import EventFilter from './EventFilter';

const EventsHeading = ({ eventTypes, setEventVisibility }) => (
  <div>
    <div className="page-header clearfix">
      <div className="row">
        <div className="col-md-8 col-xs-6">
          <h1 id="events-heading">Arrangementer</h1>
        </div>
        <div className="col-md-4 col-xs-6">
          <div className="archive-link">
            <a href={Urls.events_index()}>Arkiv
              <Glyphicon glyph="chevron-right" />
            </a>
          </div>
        </div>
      </div>
    </div>
    <div className="row">
      <div className="col-lg-12">
        <EventFilter eventTypes={eventTypes} setEventVisibility={setEventVisibility} />
      </div>
    </div>
  </div>
);

EventsHeading.propTypes = EventFilter.propTypes;


export default EventsHeading;
