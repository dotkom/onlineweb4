import React from 'react';
import { Col } from 'react-bootstrap';
import Job from './Job';

// Checks tags where the only involved factor is whether the button is on or not.
const defaultCheck = (job, id, tag) => {
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
};

  // Check for the deadline tags.
const deadlineCheck = (job, id, tag) => {
  const deadline = new Date(job.deadline);
  // If the difference between the deadline and the current date is less than the
  // deadline specified by the tag, return true.
  return deadline instanceof Date ? deadline - Date.now() <= tag.deadline : false;
};

const JobContainer = ({ jobs, tags }) => {
  const jobElems = jobs.map((job, i) => {
    // Whether we may show this job or not.
    let canShow = true;

    Object.keys(tags).forEach((type) => {
      let typeCanShow = false;

      let typeAllDisabled = true;

      Object.keys(tags[type]).forEach((tag) => {
        const tagKey = parseInt(tag, 10);

        if (tags[type][tagKey].display) {
          typeAllDisabled = false;

          const check = tags[type][tagKey].deadline ? deadlineCheck : defaultCheck;

          if (check(job, type, tags[type][tagKey])) {
            typeCanShow = true;
          }
        }
      });

      if (!(typeCanShow || typeAllDisabled)) {
        canShow = false;
      }
    });

    if (canShow) {
      return <Job {...job} key={i} />;
    }
  });

  return (
    <Col xs={12} sm={12} md={9} className="pull-left">
      {jobElems}
    </Col>
  );
};

JobContainer.propTypes = {
  jobs: React.PropTypes.arrayOf(React.PropTypes.shape({
    locations: React.PropTypes.array,
    deadline: React.PropTypes.string,
    companyImage: React.PropTypes.object,
    companyName: React.PropTypes.string,
    jobTitle: React.PropTypes.string,
    ingress: React.PropTypes.string,
    jobType: React.PropTypes.string,
    id: React.PropTypes.number,
  })),

  tags: React.PropTypes.object,
};

export default JobContainer;
