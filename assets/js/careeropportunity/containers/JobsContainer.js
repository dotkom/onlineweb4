import Job from '../components/Job';

class JobsContainer extends React.Component {
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

export default JobsContainer;
