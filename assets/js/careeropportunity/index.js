import React from 'react';
import ReactDom from 'react-dom';
import TagsContainer from './containers/TagsContainer';
import JobsContainer from './containers/JobsContainer';

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
        <div className="row">
          <div className="col-md-12">
            <div className="page-header">
              <h2>KARRIEREMULIGHETER</h2>
            </div>
          </div>
        </div>

        <div className="row">
          <div className="col-xs-12 col-sm-12 col-md-3 pull-right">
            <div className="filters">
              <h3>Bedrifter</h3>
              <TagsContainer tags={this.props.data.jobTypes} handleJobTypeChange={this.handleJobTypeChange} />
              <h3>Typer</h3>
            </div>
          </div>

          <JobsContainer jobs={this.props.data.jobs} handleJobTypeChange={this.handleJobTypeChange} ref="jobList" />
        </div>
      </div>
    );
  }
}

ReactDom.render(
  <App data={data} />,
  document.getElementById('career-container')
);
