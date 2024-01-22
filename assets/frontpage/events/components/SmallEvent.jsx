import React from 'react';
import PropTypes from 'prop-types';

const SmallEvent = ({ eventUrl, startDate, title }) => (
  <li>
    <span>
      {new Intl.DateTimeFormat("nb-NO", { month: "2-digit", day: "2-digit" }).format(startDate)}
    </span>
    <a href={eventUrl}>
      {title}
    </a>
  </li>
);

SmallEvent.propTypes = {
  eventUrl: PropTypes.string.isRequired,
  startDate: PropTypes.instanceOf(Date).isRequired,
  title: PropTypes.string.isRequired,
};

export default SmallEvent;
