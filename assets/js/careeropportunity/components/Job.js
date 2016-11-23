import React from 'react';
import { Col } from 'react-bootstrap';

const Job = ({ locations, deadline, companyImage, companyName, title, ingress, type, id }) => {
  let locationsText;

  if (locations.length >= 2) {
    locationsText = `${locations.slice(0, -1).join(', ')} og ${locations[locations.length - 1]}`;
  } else if (locations.length === 0) {
    locationsText = 'Ikke spesifisert';
  } else { // Only one location.
    locationsText = locations[0];
  }

  return (
    <article className="row">
      <Col xs={12} md={4}>
        <a href="/careeropportunity/4/">
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
            <p>Sted: {locationsText}</p>
          </Col>

          <Col md={4}>
            <p>Frist: {deadline}</p>
          </Col>
        </div>
      </Col>
    </article>
  );
};

Job.propTypes = {
  locations: React.PropTypes.arrayOf(React.PropTypes.string),
  deadline: React.PropTypes.string,
  companyImage: React.PropTypes.object,
  companyName: React.PropTypes.string,
  title: React.PropTypes.string,
  ingress: React.PropTypes.string,
  type: React.PropTypes.string,
  id: React.PropTypes.number,
};

export default Job;
