import Job from '../components/Job';

class JobContainer extends React.Component {
  constructor(props) {
    super();
  }

  render() {
    let jobs = this.props.jobs.map(function(job) {
      let canShow = true;

      for (let type in this.props.selectedTags) {
        let typeCanShow = false;

        let typeAllDisabled = true;

        for (let tag in this.props.selectedTags[type]) {
          if (this.props.selectedTags[type][tag].display) {
            typeAllDisabled = false;

            if (Array.isArray(job.tags[type])) {
              if (job.tags[type].indexOf(tag) >= 0) {
                typeCanShow = true;
              }
            } else if (job.tags[type] === tag) {
              typeCanShow = true;
            }
          }
        }

        if (!(typeCanShow || typeAllDisabled)) {
          canShow = false;
        }
      }

      if (canShow) {
        return (
          <Job {...job} />
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
