import FilterContainer from '../containers/FilterContainer';
import JobList from '../containers/JobList';
import moment from 'moment';

moment.locale('nb');

const mapData = job => ({
  locations: job.location.map(location => location.name), // Locations contains name and slug
  deadline: job.deadline ? moment(job.deadline).format('Do MMMM YYYY, HH:mm') : 'Ikke spesifisert', // Format and give default value
  companyImage: job.company.image,
  companyName: job.company.name,
  jobTitle: job.title,
  ingress: job.ingress,
  jobType: job.employment.name,
});

class FilterableJobList extends React.Component {
  constructor() {
    super();

    this.API_URL = '/api/v1/career?format=json';

    this.state = {
      jobs: [],

      tags: {
        companies: [],
        locations: [],
        jobTypes: [],
        deadlines: [],
      },
    };

    this.handleTagChange = this.handleTagChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
    this.loadData = this.loadData.bind(this);
  }

  loadData(data) {
    const self = this;

    let companies = [];
    let locations = [];
    let jobTypes = [];
    let jobs = [];

    data.results.forEach(function(job) {
      if (companies.indexOf(job.company.name) < 0) {
        companies.push(job.company);
      }

      if (jobTypes.indexOf(job.employment.name) < 0) {
        jobTypes.push(job.employment);
      }

      job.location.forEach(function(location) {
        if (locations.indexOf(location.name) < 0) {
          locations.push(location);
        }
      });

      let tagData = {
        companies: job.company.id,
        jobTypes: job.employment.id,
        locations: job.location.map((location) => location.name),
      };

      jobs.push(Object.assign({}, { tags: tagData }, mapData(job)));
    });

    let tags = {
      companies: {},
      locations: {},
      jobTypes: {},

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
    };

    companies.forEach(company => tags.companies[company.id] = { id: company.id, display: false, name: company.name });
    jobTypes.forEach(jobType => tags.jobTypes[jobType.id] = { id: jobType.id, display: false, name: jobType.name });
    locations.forEach((location, i) => tags.locations[i] = { id: i, display: false, name: location.name });

    this.setState({
      jobs: jobs,
      tags: tags,
    });

    // Store a copy of the tags for use in the reset button.
    this.defaultTags = JSON.parse(JSON.stringify(tags));
  }

  componentDidMount() {
    fetch(this.API_URL).then(response => {
      return response.json();
    }).then(this.loadData);
  }

  // TODO: Concerned about deep cloning.
  handleTagChange(type, changedTag, switchMode) {
    let self = this;

    this.setState(function(prevState) {
      let updatedState = {};

      for (let key in prevState.tags) {
        // If switchMode is on, all the other tags will be disabled - only one
        // tag may be enabled at once
        if (switchMode && key === type) {
          updatedState[type] = Object.assign({}, prevState.tags[type]);

          for (let tag in prevState.tags[type]) {
            if (tag === changedTag) {
              updatedState[type][tag].display = !updatedState[type][tag].display;
            } else {
               updatedState[type][tag].display = false;
             }
          }
        } else {
          updatedState[key] = Object.assign({}, prevState.tags[key]);
        }
      }

      if (!switchMode) {
        updatedState[type][changedTag].display = !updatedState[type][changedTag].display;
      }

      return {
        tags: updatedState
      };
    });
  }

  // Reset all buttons to their initial state.
  handleReset() {
    this.setState({
      tags: this.defaultTags,
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
          <FilterContainer tags={this.state.tags} handleTagChange={this.handleTagChange} handleReset={this.handleReset} selectedTags={this.state.tags} />
          <JobList jobs={this.state.jobs} selectedTags={this.state.tags} />
        </div>
      </div>
    );
  }
}

export default FilterableJobList;
