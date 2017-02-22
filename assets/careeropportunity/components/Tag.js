import React from 'react';
import classNames from 'classnames';

const Tag = ({ selected, title, changeKey, handleChange }) => (
  <li
    className={classNames({ selected })}
    onClick={() => handleChange(changeKey)}
  >
    {title}
  </li>
);

Tag.propTypes = {
  title: React.PropTypes.string,
  selected: React.PropTypes.bool,
  handleChange: React.PropTypes.func,
  changeKey: React.PropTypes.string,
};

export default Tag;
