import React from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

import DashboardContainer from '../../common/DashboardContainer';
import DashboardPanel from '../../common/DashboardPanel';

const ResourceDetails = ({ children, title, backUrl }) => (
  <DashboardContainer>
    <Link to={backUrl}>
      <button className="btn btn-warning">Tilbake</button>
    </Link>
    <DashboardPanel title={title}>
      { children }
    </DashboardPanel>
  </DashboardContainer>
);

ResourceDetails.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string.isRequired,
  backUrl: PropTypes.string,
};

export default ResourceDetails;
