import Job from '../components/Job';
import {Col} from 'react-bootstrap';

class JobContainer extends React.Component {
  constructor(props) {
    super();
  }

  // Checks tags where the only involved factor is whether the button is on or not.
  defaultCheck(job, id, tag) {
    // Job might have multiple tags, such as multiple locations.
    if (Array.isArray(job.tags[id])) {
      if (job.tags[id].indexOf(tag.name) >= 0) {
        return true;
      }
      // If the tag exists in the list of tags.
    } else if (job.tags[id] === tag.id) {
      return true;
    }

    return false;
  }

  // Check for the deadline tags.
  deadlineCheck(job, id, tag) {
    let deadline = new Date(job.deadline);
    // If the difference between the deadline and the current date is less than the
    // deadline specified by the tag, return true.
    return deadline instanceof Date ? deadline - Date.now() <= tag.deadline: false;
  }

  render() {
    let self = this;

    let jobs = this.props.jobs.map(function(job, i) {
      // Whether we may show this job or not.
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
      <Col xs={12} sm={12} md={9} className="pull-left">
        {jobs}
      </Col>
    );
  }
}

export default JobContainer;
