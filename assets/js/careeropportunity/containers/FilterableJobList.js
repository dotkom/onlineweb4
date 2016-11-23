import React from 'react';
import moment from 'moment';
import FilterContainer from '../containers/FilterContainer';
import JobList from '../containers/JobList';

moment.locale('nb');

// Normalizes data from the server, most notably converting to camelCase.
const mapData = job => ({
  locations: job.location.map(location => location.name), // Locations contains name and slug
  deadline: job.deadline ? moment(job.deadline).format('Do MMMM YYYY, HH:mm') : 'Ikke spesifisert', // Format and give default value
  companyImage: job.company.image,
  companyName: job.company.name,
  title: job.title,
  ingress: job.ingress,
  type: job.employment.name,
  id: job.id,
});

class FilterableJobList extends React.Component {
  constructor() {
    super();

    this.API_URL = '/api/v1/career?format=json';

    // State that will be used until data has been loaded from the server.
    this.state = {
      jobs: [],

      tags: {
        companies: {},
        locations: {},
        jobTypes: {},

        // Deadlines are not provided by the server.
        deadlines: {
          0: {
            id: 0,
            name: 'Maks 1 uke',
            display: false,
            deadline: 1000 * 60 * 60 * 24 * 7,
          },

          1: {
            id: 1,
            name: 'Maks 1 måned',
            display: false,
            deadline: 1000 * 60 * 60 * 24 * 7 * 4,
          },
        },
      },
    };

    this.handleTagChange = this.handleTagChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
    this.loadData = this.loadData.bind(this);
  }

  // Fetch data from server on component mount.
  componentDidMount() {
    fetch(this.API_URL).then(response => response.json()).then(this.loadData);
  }

  loadData(data) {
    const companies = [];
    const locations = [];
    const jobTypes = [];
    const jobs = [];

    data.results.forEach((job) => {
      // Create a new company tag if it does not already exist.
      if (companies.indexOf(job.company.name) < 0) {
        companies.push(job.company);
      }

      // Create a new employment tag if the employeer does not exist.
      if (jobTypes.indexOf(job.employment.name) < 0) {
        jobTypes.push(job.employment);
      }

      // Create tags for all non-existing locations in the job.
      job.location.forEach((location) => {
        if (locations.indexOf(location.name) < 0) {
          locations.push(location.name);
        }
      });

      // Store job tag data in an own object.
      const tagData = {
        companies: job.company.id,
        jobTypes: job.employment.id,
        // Location contains both a name and a slug.
        locations: job.location.map(location => location.name),
      };

      // Add the data to the other job properties.
      jobs.push(Object.assign({}, { tags: tagData }, mapData(job)));
    });

    const tags = {
      companies: {},
      locations: {},
      jobTypes: {},
    };

    companies.forEach((company) => {
      tags.companies[company.id] = { id: company.id, display: false, name: company.name };
    });

    jobTypes.forEach((jobType) => {
      tags.jobTypes[jobType.id] = { id: jobType.id, display: false, name: jobType.name };
    });

    locations.forEach((location, i) => {
      tags.locations[i] = { id: i, display: false, name: location };
    });

    this.setState({
      jobs,
      tags: Object.assign({}, this.state.tags, tags),
    });

    // Store a copy of the tags for use in the reset button.
    this.defaultTags = JSON.stringify(this.state.tags);
  }

  // If switchMode is true, this implies that all the tags in the TagContainer
  // should act like a select menu - selecting one tag will disselect the others.
  handleTagChange(type, changedTag, switchMode) {
    this.setState((prevState) => {
      const updatedState = {};

      Object.keys(prevState.tags).forEach((key) => {
        // If switchMode is on, all the other tags will be disabled - only one
        // tag may be enabled at once
        if (switchMode && key === type) {
          // Create a clone of the old state.
          updatedState[type] = Object.assign({}, prevState.tags[type]);

          Object.keys(prevState.tags[type]).forEach((tag) => {
            if (tag === changedTag) {
              // If this is the updated tag, toggle it. If not, turn it off.
              updatedState[type][tag].display = !updatedState[type][tag].display;
            } else {
              updatedState[type][tag].display = false;
            }
          });
        } else {
          updatedState[key] = Object.assign({}, prevState.tags[key]);
        }
      });

      // No dropdown-logic, just directly toggle the tag.
      if (!switchMode) {
        updatedState[type][changedTag].display = !updatedState[type][changedTag].display;
      }

      return {
        tags: updatedState,
      };
    });
  }

  // Reset all buttons to their initial state.
  handleReset() {
    this.setState({
      // Not creating a clone here will cause the reset button to only work once.
      tags: JSON.parse(this.defaultTags),
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
          <FilterContainer
            tags={this.state.tags}
            handleTagChange={this.handleTagChange}
            handleReset={this.handleReset}
          />

          <JobList jobs={this.state.jobs} tags={this.state.tags} />
        </div>
      </div>
    );
  }
}

export default FilterableJobList;
