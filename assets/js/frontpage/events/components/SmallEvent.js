import React from 'react';
import moment from 'moment';
import EventPropTypes from '../proptypes/EventPropTypes';

const SmallEvent = ({ event_start, id, slug, title }) => (
  <li>
    <span>
      {moment(event_start).lang('nb').format('DD.MM')}
    </span>
    <a href={`events/${id}/${slug}`}>
      {title}
    </a>
  </li>
);

SmallEvent.propTypes = {
  id: EventPropTypes.id.isRequired,
  event_start: EventPropTypes.event_start.isRequired,
  slug: EventPropTypes.slug.isRequired,
  title: EventPropTypes.title.isRequired,
};

export default SmallEvent;
