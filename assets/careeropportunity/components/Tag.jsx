import React from 'react';
import PropTypes from 'prop-types';
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
  title: PropTypes.string,
  selected: PropTypes.bool,
  handleChange: PropTypes.func,
  changeKey: PropTypes.string,
};

export default Tag;
