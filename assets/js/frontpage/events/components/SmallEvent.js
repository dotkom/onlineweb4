import React, { PropTypes } from 'react';

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

export default SmallEvent;
