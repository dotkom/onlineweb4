import React from 'react';

const InfoBox = ({ deadline, locations, jobType, contactInfo }) => (
  <div className="company">
    <div className="row">
      <div className="col-md-12">
        <div className="company-ingress">{ deadline }</div>
        <p className="pull-right company-image-caption">Trykk for mer info</p>
      </div>
    </div>
  </div>
);

export default InfoBox;
