import React, { PropTypes } from 'react';
import { FormControl } from 'react-bootstrap';

const SearchBox = ({ onChange, text }) => (
  <div>
    <h3>Filtrer</h3>
    <FormControl
      type="search"
      value={text}
      onChange={e => onChange(e)}
    />
  </div>
);

SearchBox.propTypes = {
  onChange: PropTypes.func.isRequired,
  text: PropTypes.string.isRequired,
};

export default SearchBox;
