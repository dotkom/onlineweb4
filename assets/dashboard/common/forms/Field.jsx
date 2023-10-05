import React from 'react';
import PropTypes from 'prop-types';

const Field = ({ label, name, children, required }) => (
  <div className="form-group">
    <label htmlFor={name}>{`${label}: ${required ? '*' : ''}`}</label>
    { children }
  </div>
);

Field.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  required: PropTypes.bool,
  children: PropTypes.element,
};

export default Field;
