import React from 'react';
import { Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import jobPropTypes from '../propTypes/job';

// Accepts a list of locations and returns a comma-separated list of locations
// with 'og' inserted before the last element, and 'Ikke spesifisert' if no
// locations have been specified.
export const formatLocations = (locations) => {
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
      <Link to={`/careeropportunity/${id}`}>
        <picture>
          <source srcSet={companyImage.lg} media="(max-width: 992px)" />
          <img src={companyImage.md} alt="Firmalogo" />
        </picture>
      </Link>
    </Col>

    <Col xs={12} md={8}>
      <h1>
        <Link to={`/careeropportunity/${id}`}>{companyName} - {title}</Link>
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
