import React from 'react';
import moment from 'moment';
import { Grid, Col, Row } from 'react-bootstrap';
import FilterList from '../components/FilterList';
import JobList from '../components/JobList';

// Normalizes data from the server, most notably converting to camelCase.
const normalizeData = job => ({
  locations: job.location.map(location => location.name), // Locations contains name and slug
  deadline: job.deadline ? moment(job.deadline).format('Do MMMM YYYY, HH:mm') : 'Ikke spesifisert', // Format and give default value
  companyImage: job.company.image,
  companyName: job.company.name,
  title: job.title,
  ingress: job.ingress,
  type: job.employment.name,
  id: job.id,
});

const getDeadlines = deadlines => (
  deadlines.reduce((accumulator, deadline, index) => ({
    [index]: {
      id: index,
      name: deadline.name,
      deadline: deadline.deadline,
      display: false,
    },
  }), {})
);

class FilterableJobList extends React.Component {
  constructor() {
    super();

    this.API_URL = '/api/v1/career?format=json';

    // State that will be used until data has been loaded from the server.
    this.state = {
      // List over available jobs as returned by normalizeData.
      jobs: [],

      // Stores information about a given tag, such as whether the ta
      // should be displayed in the list or not.
      tags: {
        companies: {},
        locations: {},
        jobTypes: {},

        // Deadlines are not provided by the server.
        deadlines: getDeadlines([
          {
            name: 'Maks 1 uke',
            deadline: 1000 * 60 * 60 * 24 * 7,
          },

          {
            name: 'Maks 1 måned',
            deadline: 1000 * 60 * 60 * 24 * 7 * 4,
          },
        ]),
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

  // Parses received data and updates the state.
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

      // Add information to the job that is used to filter using tags.
      jobs.push(Object.assign({}, { tags: {
        companies: job.company.id,
        jobTypes: job.employment.id,
        locations: job.location.map(location => location.name),
      } }, normalizeData(job)));
    });

    // Update the tags with new information from the server.
    // Deadlines are not updated here as they're specified in the initial state.
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

  // Handles a tag button being clicked by updating the state of the tag with id
  // changedTag of the specified type. If switchMode is true, all the tags in the TagContainer
  // will behave like a kind select menu - selecting one tag will blur all the other buttons.
  // This is used with the deadline tags, as selecting both 1 week and 1 month at the same
  // time makes little sense.
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
              // This is the updated tag, so we toggle it.
              updatedState[type][tag].display = !updatedState[type][tag].display;
            } else {
              // This is not the updated tag, so we set it to false.
              updatedState[type][tag].display = false;
            }
          });
        } else {
          // Copy the state over from the previous state.
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
      <Grid>
        <Row>
          <Col md={4}>
            <div className="page-header">
              <h2>KARRIEREMULIGHETER</h2>
            </div>
          </Col>
        </Row>

        <Row>
          <FilterList
            tags={this.state.tags}
            handleTagChange={this.handleTagChange}
            handleReset={this.handleReset}
          />

          <JobList jobs={this.state.jobs} tags={this.state.tags} />
        </Row>
      </Grid>
    );
  }
}

export default FilterableJobList;
