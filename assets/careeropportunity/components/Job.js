import React from 'react';
import { Col } from 'react-bootstrap';
import jobPropTypes from '../propTypes/job';

// Accepts a list of locations and returns a comma-separated list of locations
// with 'og' inserted before the last element, and 'Ikke spesifisert' if no
// locations have been specified.
const formatLocations = (locations) => {
  if (locations.length >= 2) { // If we have more than 2 elements, return a comma-separated list.
    return `${locations.slice(0, -1).join(', ')} og ${locations[locations.length - 1]}`;
  } else if (locations.length === 1) { // Do not format the location if we only have 1 element.
    return locations[0];
  }

  // No locations have been specified.
  return 'Ikke spesifisert';
};

const Job = ({ locations, deadline, companyImage, companyName, title, ingress, type, id }) => (
  <article className="row">
    <Col xs={12} md={4}>
      <a href={`/careeropportunity/${id}`}>
        <picture>
          <source srcSet={companyImage.lg} media="(max-width: 992px)" />
          <img src={companyImage.md} alt="Firmalogo" />
        </picture>
      </a>
    </Col>

    <Col xs={12} md={8}>
      <h1>
        <a href={`/careeropportunity/${id}`}>{companyName} - {title}</a>
      </h1>

      <div className="ingress">{ingress}</div>

      <div className="meta">
        <Col md={4}>
          <p>Type: {type}</p>
        </Col>

        <Col md={4}>
          <p>Sted: {formatLocations(locations)}</p>
        </Col>

        <Col md={4}>
          <p>Frist: {deadline}</p>
        </Col>
      </div>
    </Col>
  </article>
  );

Job.propTypes = jobPropTypes;

export default Job;
