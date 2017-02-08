import React from 'react';
import '../css/business.css';

const BusinessProfiling = () => (
	<div className="col-sm-5 col-md-6">
    <div className="row">
      <div className="col-md-6">
          <div className="col-md-12 sale-box">
            <div className="sale-heading">Profilering</div>
          </div>
          <div className="col-md-12 sale-content">
            <ul className="list-unstyled sale-points">
              <li><span className="glyphicon glyphicon-ok"></span> Bedriftspresentasjon</li>
              <li><span className="glyphicon glyphicon-ok"></span> Annonse i Offline</li>
              <li><span className="glyphicon glyphicon-ok"></span> Stillingsutlysning</li>
            </ul>
            <div className="link center-text">
              <a href="#business-profiling" data-toggle="modal">Les mer</a>
            </div>
          </div>
      </div>
      <div className="col-md-6">
        <div className="col-md-12 sale-box">
          <div className="sale-heading">Faglig</div>
        </div>
        <div className="col-md-12 sale-content">
          <ul className="list-unstyled sale-points">
            <li><span className="glyphicon glyphicon-ok"></span> Kurs/kursserie</li>
            <li><span className="glyphicon glyphicon-ok"></span> Workshop</li>
            <li><span className="glyphicon glyphicon-ok"></span> Hackathon</li>
          </ul>
          <div className="link center-text">
            <a href="#business-academic" data-toggle="modal">Les mer</a>
          </div>
        </div>
      </div>
    </div>
  </div>
);


export default BusinessProfiling;