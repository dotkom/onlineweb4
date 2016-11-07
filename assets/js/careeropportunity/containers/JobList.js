import Job from '../components/Job';

class JobContainer extends React.Component {
  constructor(props) {
    super();
  }

  render() {
    let jobs = this.props.jobs.map(function(job) {
      let canShow = true;

      for (let type in this.props.selectedTags) {
        for (let tag in this.props.selectedTags[type]) {
          if (this.props.selectedTags[type][tag]) {
            if (Array.isArray(job[type])) {
              if (job[type].indexOf(tag) < 0) {
                canShow = false;
              }
            } else if (job[type] !== tag) {
              canShow = false;
            }
          }
        }
      }

      if (canShow) {
        return (
          <Job jobData={job.data} />
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
