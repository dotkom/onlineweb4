import React from 'react';
import PropTypes from 'prop-types';

import Field from './Field';

const BooleanInput = ({ name, value, label, onChange, required }) => {
  const handleChange = (event) => {
    onChange(name, event.target.checked);
  };

  return (
    <Field name={name} label={label} required={required}>
      <input
        id={name}
        name={name}
        type="checkbox"
        onChange={handleChange}
        checked={value}
      />
    </Field>
  );
};

BooleanInput.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.bool.isRequired,
  label: PropTypes.string.isRequired,
  required: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
};

export default BooleanInput;
