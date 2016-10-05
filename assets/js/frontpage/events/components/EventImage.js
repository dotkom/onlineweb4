import React from 'react';
import classNames from 'classnames';

const EventImage = ({ event_start, id, images, slug }) => {
  return (
    <div className="col-sm-4 col-md-2" id="eventimage">
      <div id="event-carousel" className="carousel slide">
        <div className="carousel-inner">
            { images.map((image, index) => (
              <div className={ classNames('item', { active: index === 0 }) }>
                <a href={ `events/${id}/${slug}` }>
                  <img src={ `https://online.ntnu.no/${image}` } width="100%" alt=""/>
                </a>
              </div>
            ))
          }
        </div>
      </div>
      <span className="hero-date">{ moment(event_start).lang('nb').format('DD. MMMM') }</span>
    </div>
  )
};

export default EventImage;
