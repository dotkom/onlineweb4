import JobTypeButton from '../components/JobTypeButton';

class JobTypeButtonsContainer extends React.Component {
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
        <JobTypeButton selected={this.state.selectedJobTypes[jobType.key]} jobType={jobType.key} handleChange={this.handleChange} title={jobType.title} />
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

export default JobTypeButtonsContainer;
