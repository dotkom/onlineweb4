import React from 'react';

const Header = () => (
  <div className="page-header clearfix">
      <div className="row">
          <div className="col-md-8 col-xs-6">
              <h2 id="events-heading">ARRANGEMENTER</h2>
          </div>
          <div className="col-md-4 col-xs-6 archive-link">
              <a href="/events">ARKIV
                  <i className="glyphicon glyphicon-chevron-right"></i>
              </a>
          </div>
      </div>
  </div>
);

export default Header;
