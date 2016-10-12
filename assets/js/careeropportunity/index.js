import React from 'react';
import ReactDom from 'react-dom';
import { DropdownButton } from 'react-bootstrap';
import { MenuItem } from 'react-bootstrap';

const App = () => (
  <DropdownButton>
    <MenuItem>1</MenuItem>
    <MenuItem>2</MenuItem>
    <MenuItem>3</MenuItem>
  </DropdownButton>
);

ReactDom.render(
  <App />,
  document.getElementById('careeropportunities')
);
