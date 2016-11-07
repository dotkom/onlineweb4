import React from 'react';
import FilterContainer from '../containers/FilterContainer';
import JobList from '../containers/JobList';
import request from 'superagent';

class CareerContainer extends React.Component {
  constructor() {
    super();

    this.state = {
      jobs: [],

      tags: {
        companies: [],
        locations: [],
        jobTypes: []
      },

      selectedTags: {
        companies: {},
        locations: {},
        jobTypes: {}
      }
    };

    this.defaultSelectedtags = Object.assign({}, this.state.selectedTags);

    this.handleTagChange = this.handleTagChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
  }


  componentDidMount() {
    const self = this;

    request('GET', '/api/v1/career/').then(function(response) {
      let data = JSON.parse(response.text);

      let companies = [];
      let locations = [];
      let jobTypes = [];
      let jobs = [];

      data.results.forEach(function(job) {
        if (companies.indexOf(job.company.name) < 0) {
          companies.push(job.company.name);
        }

        if (jobTypes.indexOf(job.employment.name) < 0) {
          jobTypes.push(job.employment.name);
        }

        job.location.forEach(function(location) {
          if (locations.indexOf(location.name) < 0) {
            locations.push(location.name);
          }
        });

        jobs.push({
          companies: job.company.name,
          jobTypes: job.employment.name,
          locations: job.location.map((location) => location.name),
          data: job
        });
      });

      self.setState({
        jobs: jobs,

        tags: {
          companies: companies,
          locations: locations,
          jobTypes: jobTypes
        }
      });
    });
  }

  handleTagChange(type, tag) {
    let self = this;

    this.setState(function(prevState) {
      let updatedState = {};

      for (let key in prevState.selectedTags) {
        updatedState[key] = prevState.selectedTags[key];
      }

      updatedState[type][tag] = !updatedState[type][tag];

      return {
        selectedTags: updatedState
      };
    });
  }

  // Reset all buttons to their initial state.
  handleReset() {
    this.setState({
      selectedTags: this.defaultSelectedtags
    });
  }

  render() {
    return (
      <section id="career">
        <div className="container">
          <div className="row">
            <div className="col-md-12">
              <div className="page-header">
                <h2>KARRIEREMULIGHETER</h2>
              </div>
            </div>
          </div>

          <div className="row">
            <FilterContainer tags={this.state.tags} handleTagChange={this.handleTagChange} selectedTags={this.state.selectedTags} />
            <JobList jobs={this.state.jobs} selectedTags={this.state.selectedTags} />
          </div>
        </div>
      </section>
    );
  }
}

export default CareerContainer;
