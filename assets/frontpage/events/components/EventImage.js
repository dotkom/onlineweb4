import React, { PropTypes } from 'react';
import moment from 'moment';
import { Carousel } from 'react-bootstrap';
import ImagePropTypes from 'common/proptypes/ImagePropTypes';

const EventImage = ({ date, eventUrl, images }) => (
  <div className="col-sm-4 col-md-2">
    <Carousel controls={false} indicators={false}>
      { images.map((image, index) => (
        <Carousel.Item key={index} active={index === 0}>
          <a href={eventUrl}>
            <picture>
              <source srcSet={image.lg} media="(max-width: 768px)" />
              <source srcSet={image.md} media="(max-width: 992px)" />
              <img src={image.thumb} width="100%" alt="" />
            </picture>
          </a>
        </Carousel.Item>
        ))
      }
    </Carousel>
    <span className="hero-date">{ moment(date).format('DD. MMMM') }</span>
  </div>
);

EventImage.propTypes = {
  date: PropTypes.string.isRequired,
  eventUrl: PropTypes.string.isRequired,
  images: PropTypes.arrayOf(ImagePropTypes),
};

export default EventImage;
