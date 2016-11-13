import React, { PropTypes } from 'react';
import moment from 'moment';

const SmallEvent = ({ eventUrl, startDate, title }) => (
  <li>
    <span>
      {moment(startDate).lang('nb').format('DD.MM')}
    </span>
    <a href={eventUrl}>
      {title}
    </a>
  </li>
);

SmallEvent.propTypes = {
  eventUrl: PropTypes.string.isRequired,
  startDate: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
};

export default SmallEvent;
