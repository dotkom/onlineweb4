import React from 'react';
import PropTypes from 'prop-types';

const DashboardContainer = ({ children }) => (
  <div className="row">
    <div className="col-lg-12">
      { children }
    </div>
  </div>
);

DashboardContainer.propTypes = {
  children: PropTypes.node.isRequired,
};

export default DashboardContainer;
