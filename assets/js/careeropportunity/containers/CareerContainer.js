import React from 'react';
import TagContainer from '../containers/TagContainer';
import JobList from '../containers/JobList';

let data = {
  jobs: [{
    title: 'Jobb',
    jobType: 0,
    company: 0,
    location: 0
  }, {
    title: 'Konsulent',
    jobType: 1,
    company: 1,
    location: 0
  }, {
    title: 'Slave',
    jobType: 2,
    company: 2,
    location: 0
  }],

  jobTypes: [{
    key: 0,
    title: 'Sommerjobb'
  }, {
    key: 1,
    title: 'Fulltidsjobb'
  }, {
    key: 2,
    title: 'Deltidsjobb'
  }],

  companies: [{
    key: 0,
    title: 'Accenture'
  }, {
    key: 1,
    title: 'Sopra Steria'
  }, {
    key: 2,
    title: 'Mamma'
  }],

  locations: [{
    key: 0,
    title: 'Trondheim'
  }]
};

class CareerContainer extends React.Component {
  constructor() {
    super();

    this.state = {
      jobs: data.jobs,
      jobTypes: data.jobTypes,
      companies: data.companies,
      locations: data.locations,
      selectedTags: {}
    };

    this.handleTagChange = this.handleTagChange.bind(this);

    this.handleJobTypeChange = this.handleJobTypeChange.bind(this);
    this.handleCompanyChange = this.handleCompanyChange.bind(this);
    this.handleLocationChange = this.handleLocationChange.bind(this);
  }

  handleTagChange(type, updatedValues) {
    let updatedState = {};

    updatedState[type] = updatedValues;

    this.setState({
      selectedTags: updatedState
    });
  }

  handleJobTypeChange(updated) {
    this.handleTagChange('jobType', updated);
  }

  handleCompanyChange(updated) {
    this.handleTagChange('company', updated);
  }

  handleLocationChange(updated) {
    this.handleTagChange('location', updated);
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
              <TagContainer heading="Bedrifter" tags={this.state.companies} handleChange={this.handleCompanyChange} />
              <TagContainer heading="Typer" tags={this.state.jobTypes} handleChange={this.handleJobTypeChange} />
              <TagContainer heading="Sted" tags={this.state.locations} handleChange={this.handleLocationChange} />
            </div>
          </div>

          <JobList jobs={this.state.jobs} selectedTags={this.state.selectedTags} />
        </div>
      </div>
    );
  }
}

export default CareerContainer;
