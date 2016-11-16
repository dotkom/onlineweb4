import Job from '../components/Job';

class JobContainer extends React.Component {
  constructor(props) {
    super();
  }

  render() {
    let jobs = this.props.jobs.map(function(job, i) {
      let canShow = true;

      for (let id in this.props.selectedTags) {
        let typeCanShow = false;

        let typeAllDisabled = true;

        for (let tag in this.props.selectedTags[id]) {
          tag = parseInt(tag, 10);

          if (this.props.selectedTags[id][tag].display) {
            typeAllDisabled = false;

            if (Array.isArray(job.tags[id])) {
              if (job.tags[id].indexOf(tag) >= 0) {
                typeCanShow = true;
              }
            } else if (job.tags[id] === tag) {
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
          <Job {...job} key={i} /> // TODO: Store a key while JSON parsing?
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
