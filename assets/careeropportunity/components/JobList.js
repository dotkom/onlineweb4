import React from 'react';
import { Col } from 'react-bootstrap';
import moment from 'moment';
import Job from './Job';
import tagsPropTypes from '../propTypes/tags';
import jobPropTypes from '../propTypes/job';

// Checks tags where the only involved factor is whether the button is on or not.
const defaultCheck = (job, id, tag) => {
  // Job might have multiple tags, such as multiple locations.
  if (Array.isArray(job.tags[id])) {
    // If the tag exists in the list of tags.
    if (job.tags[id].indexOf(tag.name) >= 0) {
      return true;
    }
  } else if (job.tags[id] === tag.id) {
    return true;
  }

  return false;
};

// Check for the deadline tags. If the difference between the deadline, and
// the current date is less than the deadline specified by the tag, return true.
const deadlineCheck = (job, id, tag) => (
  moment().isValid(job.deadline) ?
    new Date(job.deadline).getTime() - Date.now() <= tag.deadline : false
);

const JobList = ({ jobs, tags }) => {
  const jobElems = jobs.reduce((elems, job, i) => {
    // Whether we may show this job or not.
    let canShow = true;

    Object.keys(tags).forEach((type) => {
      // If this value is true, it means the job contains all the
      // selected tags in the current group of tags.
      let typeCanShow = false;

      // True if no tags in the current tag type are selected.
      let typeAllDisabled = true;

      Object.keys(tags[type]).forEach((tag) => {
        if (tags[type][tag].display) {
          typeAllDisabled = false;

          // If this is a deadline, we use a date-based checking function instead.
          const check = tags[type][tag].deadline ? deadlineCheck : defaultCheck;

          // Checks if the job can displayed based on the current tag or not.
          if (check(job, type, tags[type][tag])) {
            typeCanShow = true;
          }
        }
      });

      if (!(typeCanShow || typeAllDisabled)) {
        canShow = false;
      }
    });

    if (canShow) {
      elems.push(<Job {...job} key={i} />);
    }

    return elems;
  }, []);

  return (
    <Col xs={12} sm={12} md={9} className="pull-left">
      {jobElems}
    </Col>
  );
};

JobList.propTypes = {
  jobs: React.PropTypes.arrayOf(React.PropTypes.shape(jobPropTypes)),
  tags: tagsPropTypes,
};

export default JobList;
