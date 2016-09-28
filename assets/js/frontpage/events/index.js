import React from 'react';
import ReactDom from 'react-dom';

const App = () => (
  <div className="container">
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
      <div id="event-items">
        Hello World
      </div>
  </div>
);

ReactDom.render(
  <App />,
  document.getElementById('events')
);
