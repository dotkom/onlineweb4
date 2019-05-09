import React from 'react';
import PropTypes from 'prop-types';

import Field from './Field';

const NumberInput = ({ name, value, label, onChange, required, placeholder }) => {
  const handleChange = (event) => {
    onChange(name, Number(event.target.value));
  };

  return (
    <Field name={name} label={label} required={required}>
      <input
        id={name}
        name={name}
        type="number"
        onChange={handleChange}
        value={value}
        placeholder={placeholder}
        className="form-control"
      />
    </Field>
  );
};

NumberInput.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
  label: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
};

export default NumberInput;
