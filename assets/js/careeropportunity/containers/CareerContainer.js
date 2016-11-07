import React from 'react';
import FilterContainer from '../containers/FilterContainer';
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

      tags: {
        companies: data.companies,
        locations: data.locations,
        jobTypes: data.jobTypes
      },

      selectedTags: {}
    };

    this.handleTagChange = this.handleTagChange.bind(this);
  }

  handleTagChange(type, updatedValues) {
    let updatedState = {};

    updatedState[type] = updatedValues;

    this.setState({
      selectedTags: updatedState
    });
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
          <FilterContainer tags={this.state.tags} handleTagChange={this.handleTagChange} />
          <JobList jobs={this.state.jobs} selectedTags={this.state.selectedTags} />
        </div>
      </div>
    );
  }
}

export default CareerContainer;
