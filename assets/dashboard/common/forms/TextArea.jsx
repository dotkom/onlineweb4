import React from 'react';
import PropTypes from 'prop-types';

import Field from './Field';

const TextArea = ({ name, value, label, onChange, required, placeholder }) => {
  const handleChange = (event) => {
    onChange(name, event.target.value);
  };

  return (
    <Field name={name} label={label} required={required}>
      <textarea
        id={name}
        name={name}
        onChange={handleChange}
        value={value}
        className="form-control"
        placeholder={placeholder}
        rows="10"
        cols="40"
      />
    </Field>
  );
};

TextArea.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
};

export default TextArea;
