import React from 'react';
import classNames from 'classnames';

const Tag = ({ selected, title, changeKey, handleChange }) => (
  <button
    className={classNames({ selected })}
    onClick={() => handleChange(changeKey)}
  >
    {title}
  </button>
);

Tag.propTypes = {
  title: React.PropTypes.string,
  selected: React.PropTypes.bool,
  handleChange: React.PropTypes.func,
  changeKey: React.PropTypes.string,
};

export default Tag;
