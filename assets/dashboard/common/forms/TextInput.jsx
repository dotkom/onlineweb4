import React from 'react';
import PropTypes from 'prop-types';

import Field from './Field';

const TextInput = ({ name, value, label, onChange, required, placeholder }) => {
  const handleChange = (event) => {
    onChange(name, event.target.value);
  };

  return (
    <Field name={name} label={label} required={required}>
      <input
        id={name}
        name={name}
        type="text"
        onChange={handleChange}
        value={value}
        className="form-control"
        placeholder={placeholder}
      />
    </Field>
  );
};

TextInput.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
};

export default TextInput;
