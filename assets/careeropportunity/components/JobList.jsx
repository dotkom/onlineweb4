import React from 'react';
import PropTypes from 'prop-types';
import { Col } from 'react-bootstrap';
import moment from 'moment';
import Fuse from 'fuse.js';
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

// Move jobs which match the check to the top of the array using
// a stable algorithm. This is used to move full-time jobs and
// sponsored jobs to the top.
const arrangeJobs = (jobs, check) => {
  const top = [];
  const remainder = [];

  jobs.forEach((job) => {
    if (check(job)) {
      top.push(job);
    } else {
      remainder.push(job);
    }
  });

  return top.concat(remainder);
};

// Check for the deadline tags. If the difference between the deadline, and
// the current date is less than the deadline specified by the tag, return true.
const deadlineCheck = (job, id, tag) => (
  moment().isValid(job.deadline) ?
    new Date(job.deadline).getTime() - Date.now() <= tag.deadline : false
);

const JobList = ({ jobs, tags, filterText }) => {
  const fuse = new Fuse(jobs, {
    shouldSort: false,
    treshold: 0.6,
    location: 0,
    distance: 100,
    maxPatternLength: 32,
    minMatchCharLength: 1,
    keys: [
      'locations', 'companyName', 'companyName', 'title', 'ingress', 'type',
    ],
  });

  const search = fuse.search(filterText);

  const prefilteredJobs = filterText.length ? search : jobs;

  let jobObjects = prefilteredJobs.reduce((elems, job) => {
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
      elems.push(job);
    }

    return elems;
  }, []);

  if (!filterText) {
    jobObjects = jobObjects.sort((a, b) => a.title > b.title);
  }

  // First move full-time jobs to the top, then move the sponsored
  // jobs to the top, while retaining the full-time-job sorting.
  const sortedJobs = arrangeJobs(
    arrangeJobs(jobObjects, job => job.type === 'Fastjobb'), job => job.featured,
  );

  const jobElems = sortedJobs.map((job, i) => <Job {...job} key={i} />);

  return (
    <Col xs={12} sm={12} md={9} className="pull-left">
      {jobElems}
    </Col>
  );
};

JobList.propTypes = {
  jobs: PropTypes.arrayOf(PropTypes.shape(jobPropTypes)),
  tags: tagsPropTypes,
  filterText: PropTypes.string.isRequired,
};

export default JobList;
