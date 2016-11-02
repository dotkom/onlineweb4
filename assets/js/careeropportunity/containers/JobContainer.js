import Job from '../components/Job';

class JobContainer extends React.Component {
  constructor(props) {
    super();

    this.state = {
      selectedJobTypes: {},
      selectedTags: {}
    };
  }

  handleTagChange(type, updatedValues) {
    let updatedState = {};

    updatedState[type] = updatedValues;

    this.setState({
      selectedTags: updatedState
    });
  }

  render() {
    let jobs = this.props.jobs.map(function(job) {
      let canShow = true;

      for (let type in this.state.selectedTags) {
        for (let key in this.state.selectedTags[type]) {
          if (this.state.selectedTags[type][key]) {
            if (Array.isArray(job[type]) && job[type].indexOf(this.state.selectedTags[type][key]) < 0) {
              canShow = false;
            } else if (job[type] !== parseInt(key, 10)) { // :O :O :O :O TODO, parseInt should not be needed - move away from number keys?
              canShow = false;
            }
          }
        }
      }

      if (canShow) {
        return (
          <Job jobTitle={job.title} />
        );
      }
    }.bind(this));

    return (
      <div className="col-xs-12 col-sm-12 col-md-9 pull-left">
        {jobs}
      </div>
    );
  }
}

export default JobContainer;
