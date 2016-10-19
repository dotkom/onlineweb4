import React from 'react';
import ReactDom from 'react-dom';

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

class Job extends React.Component {
  constructor() {
    super();
  }

  render() {
    return (
      <div className="job">
        {this.props.jobTitle}
      </div>
    );
  }
}

class JobList extends React.Component {
  constructor(props) {
    super();

    this.state = {
      selectedJobTypes: {}
    };

    this.handleJobTypeChange = this.handleJobTypeChange.bind(this);
  }

  handleJobTypeChange(selectedJobTypes) {
    this.setState({
      selectedJobTypes: selectedJobTypes
    });
  };

  render() {
    // Warning: Will be true on the initial render, which is the reason as to why we can
    // have an empty object in the initial selectedJobTypes state!
    let allJobTypesDisabled = true;

    for (let key in this.state.selectedJobTypes) {
      if (this.state.selectedJobTypes.hasOwnProperty(key) && this.state.selectedJobTypes[key] === true) {
        allJobTypesDisabled = false;
      }
    }

    let jobs = this.props.jobs.map(function(job) {
      if (this.state.selectedJobTypes[job.type] || allJobTypesDisabled) {
        return (
          <Job jobTitle={job.title} />
        );
      }
    }.bind(this));

    return (
      <div class="job-list">
        {jobs}
      </div>
    );
  }
}

class JobType extends React.Component {
  constructor() {
    super();

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(key) {
    this.props.handleChange(key);
  }

  render() {
    return (
      <button onClick={this.handleClick.bind(this, this.props.jobType)}>{this.props.title} - {this.props.selected ? 'yes' : 'no'}</button>
    );
  }
}

class JobTypeMenu extends React.Component {
  constructor(props) {
    super();

    this.state = {
      selectedJobTypes: {}
    };

    for (let key in props.jobTypes) {
      if (props.jobTypes.hasOwnProperty(key)) {
        this.state.selectedJobTypes[key] = false;
      }
    }

    this.handleChange = this.handleChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
  }

  handleChange(selectedKey) {
    let selectedJobTypes = this.state.selectedJobTypes;

    selectedJobTypes[selectedKey] = !selectedJobTypes[selectedKey];

    this.setState({
      selectedJobTypes: selectedJobTypes
    });

    this.props.handleJobTypeChange(selectedJobTypes);
  }

  handleReset() {
    let resetJobTypes = {};

    for (let key in this.state.selectedJobTypes) {
      if (this.state.selectedJobTypes.hasOwnProperty(key)) {
        resetJobTypes[key] = false;
      }
    }

    this.setState({
      selectedJobTypes: resetJobTypes
    });

    this.props.handleJobTypeChange(resetJobTypes);
  }

  render() {
    let jobTypeButtons = this.props.jobTypes.map(function(jobType) {
      return (
        <JobType selected={this.state.selectedJobTypes[jobType.key]} jobType={jobType.key} handleChange={this.handleChange} title={jobType.title} />
      );
    }.bind(this));

    return (
      <div>
        {jobTypeButtons}
        <button onClick={this.handleReset}>reset</button>
      </div>
    );
  }
}

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
            <JobList jobs={this.props.data.jobs} handleJobTypeChange={this.handleJobTypeChange} ref="jobList" />
          </div>

          <div className="col-md-4">
            <JobTypeMenu jobTypes={this.props.data.jobTypes} handleJobTypeChange={this.handleJobTypeChange} />
          </div>
      </div>
    );
  }
}

ReactDom.render(
  <App data={data} />,
  document.getElementById('careeropportunities')
);
