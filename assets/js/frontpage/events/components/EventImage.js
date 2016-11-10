import React from 'react';
import { Carousel } from 'react-bootstrap';
import classNames from 'classnames';

const EventImage = ({ event_start, id, images, slug }) =>
   (
     <div className="col-sm-4 col-md-2">
       <Carousel controls={false} indicators={false}>
         { images.map((image, index) => (
           <Carousel.Item key={index} active={index === 0}>
             <a href={`events/${id}/${slug}`}>
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
       <span className="hero-date">{ moment(event_start).lang('nb').format('DD. MMMM') }</span>
     </div>
  )
;

export default EventImage;
