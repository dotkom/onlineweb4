import React from 'react';
import { Carousel } from 'react-bootstrap';
import classNames from 'classnames';

const EventImage = ({ event_start, id, images, slug }) => {
  return (
    <div className="col-sm-4 col-md-2">
      <Carousel controls={ false } indicators={ false }>
          { images.map((image, index) => (
            <Carousel.Item active={index === 0 }>
              <a href={ `events/${id}/${slug}` }>
                <img src={ image } width="100%" alt=""/>
              </a>
            </Carousel.Item>
          ))
        }
      </Carousel>
      <span className="hero-date">{ moment(event_start).lang('nb').format('DD. MMMM') }</span>
    </div>
  )
};

export default EventImage;
