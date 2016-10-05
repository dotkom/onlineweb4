import React from 'react';

const EventImage = ({ event_start, id, images, slug }) => (
  <div className="col-sm-4 col-md-2" id="eventimage">
    <div id="event-carousel" className="carousel slide">
      <div className="carousel-inner">
          { images.length > 0
            ? (
              <div className="item active">
                <a href={ `events/${id}/${slug}` }>
                  <img src={ `https://online.ntnu.no/${images[0]}` } width="100%" alt=""/>
                </a>
              </div>
            )
            : null
          }
      </div>
    </div>
    <span className="hero-date">{ moment(event_start).lang('nb').format('DD. MMMM') }</span>
  </div>
);

export default EventImage;
