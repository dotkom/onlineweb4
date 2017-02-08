import React from 'react';
import BusinessText from './BusinessText';
import BusinessHeading from './BusinessHeading';
import BusinessProfiling from './BusinessProfiling';

const Business = ({ mainBusiness, smallBusiness }) => (
  <div>
    <BusinessHeading />
    <div className="row">
      <BusinessText />
      <BusinessProfiling />
    </div>
  </div>
);


export default Business;