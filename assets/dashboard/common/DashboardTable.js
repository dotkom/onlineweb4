import React from 'react';
import PropTypes from 'prop-types';

const DashboardTable = ({ children, headers = [] }) => (
  <table className="table table-striped table-condensed tablesorter">
    <thead>
      <tr>
        { headers.map(header => <th>{ header }</th>) }
      </tr>
    </thead>
    <tbody>
      { children }
    </tbody>
  </table>
);

DashboardTable.propTypes = {
  children: PropTypes.node,
  headers: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default DashboardTable;
