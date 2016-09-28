import React from 'react';

const EventImage = ({ date }) => (
  <div className="col-sm-4 col-md-2" id="eventimage">
    <div id="event-carousel" className="carousel slide">
      <div className="carousel-inner">
        <div className="item active">
          <img />
        </div>
      </div>
    </div>
    <span className="hero-date">{ date }</span>
  </div>
);

export default EventImage;
