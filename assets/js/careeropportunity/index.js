import React from 'react';
import ReactDom from 'react-dom';
import JobTypeButtonsContainer from './containers/JobTypeButtonsContainer';
import JobsContainer from './containers/JobsContainer.js';

let data = {
  jobs: [{
    title: 'accenture',
    type: 0
  }, {
    title: 'sopra steria',
    type: 1
  }, {
    title: 'slave hjå mamma',
    type: 2
  }],

  jobTypes: [{
    key: 0,
    title: 'Jobs'
  }, {
    key: 1,
    title: 'More jobs'
  }, {
    key: 2,
    title: 'Great jobs'
  }]
};

class App extends React.Component {
  constructor(data) {
    super();

    this.handleJobTypeChange = this.handleJobTypeChange.bind(this);
  }

  handleJobTypeChange(type) {
    this.refs.jobList.handleJobTypeChange(type);
  }

  render() {
    return (
      <div className="container">
          <div className="page-header clearfix">
              <div className="row">
                  <div className="col-md-8 col-xs-6">
                      <h2 id="events-heading">KARRIEREMULIGHETER</h2>
                  </div>
              </div>
          </div>

          <div className="col-md-8">
            <JobsContainer jobs={this.props.data.jobs} handleJobTypeChange={this.handleJobTypeChange} ref="jobList" />
          </div>

          <div className="col-md-4">
            <JobTypeButtonsContainer jobTypes={this.props.data.jobTypes} handleJobTypeChange={this.handleJobTypeChange} />
          </div>
      </div>
    );
  }
}

ReactDom.render(
  <App data={data} />,
  document.getElementById('careeropportunities')
);
