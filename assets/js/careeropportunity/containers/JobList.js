import Job from '../components/Job';

class JobContainer extends React.Component {
  constructor(props) {
    super();
  }

  defaultCheck(job, id, tag) {
    if (Array.isArray(job.tags[id])) {
      if (job.tags[id].indexOf(tag.name) >= 0) {
        return true;
      }
    } else if (job.tags[id] === tag.id) {
      return true;
    }

    return false;
  }

  deadlineCheck(job, id, tag) {
    let deadline = new Date(job.deadline);
    return deadline instanceof Date ? deadline - Date.now() <= tag.deadline: false;
  }

  render() {
    let self = this;

    let jobs = this.props.jobs.map(function(job, i) {
      let canShow = true;

      for (let type in this.props.tags) {
        let typeCanShow = false;

        let typeAllDisabled = true;

        for (let key in this.props.tags[type]) {
          key = parseInt(key, 10);

          if (this.props.tags[type][key].display) {
            typeAllDisabled = false;

            let check = this.props.tags[type][key].deadline ? self.deadlineCheck : self.defaultCheck;

            if (check(job, type, this.props.tags[type][key])) {
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
