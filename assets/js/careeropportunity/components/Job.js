import {Col} from 'react-bootstrap';

const Job = ({ locations, deadline, companyImage, companyName, jobTitle, ingress, jobType, id }) => {
  if (locations.length >= 2) {
    locations = `${locations.slice(0, -1).join(', ')} og ${locations[locations.length - 1]}`;
  } else if (locations.length === 0) {
    locations = 'Ikke spesifisert';
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
          <a href={'/careeropportunity/' + id}>{companyName} - {jobTitle}</a>
        </h1>

        <div className="ingress">{ingress}</div>

        <div className="meta">
          <Col md={4}>
            <p>Type: {jobType}</p>
          </Col>

          <Col md={4}>
            <p>Sted: {locations}</p>
          </Col>

          <Col md={4}>
            <p>Frist: {deadline}</p>
          </Col>
        </div>
      </Col>
    </article>
  );
};

export default Job;
