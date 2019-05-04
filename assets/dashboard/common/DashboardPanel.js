import React from 'react';
import PropTypes from 'prop-types';

const DashboardPanel = ({ children, title }) => (
  <div className="panel panel-default">
    <div className="panel-heading">
      <h3 className="panel-title">{title}</h3>
    </div>
    <div className="panel-body">
      { children }
    </div>
  </div>
);

DashboardPanel.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string.isRequired,
};

export default DashboardPanel;
