import moment from 'moment';

moment.locale('nb');

const Job = ({ locations, deadline, companyImage, companyName, jobTitle, ingress, jobName }) => {
  if (locations.length >= 2) {
    locations = `${locations.slice(0, -1).join(', ')} and ${locations[locations.length - 1]}`;
  } else if (locations.length === 0) {
    locations = 'Ikke spesifisert';
  }

  return (
    <article className="row">
      <div className="col-xs-12 col-md-4">
        <a href="/careeropportunity/4/">
          <picture>
            <source srcset={companyImage.lg} media="(max-width: 992px)" />
            <img src={companyImage.md} alt="Firmalogo" />
          </picture>
        </a>
      </div>

      <div className="col-xs-12 col-md-8">
        <h1>
          <a href="/careeropportunity/4/">{companyName} - {jobTitle}</a>
        </h1>

        <div className="ingress">{ingress}</div>

        <div className="meta">
          <div className="col-md-4">
            <p>Type: {jobName}</p>
          </div>

          <div className="col-md-4">
            <p>Sted: {locations}</p>
          </div>

          <div className="col-md-4">
            <p>Frist: {deadline}</p>
          </div>
        </div>
      </div>
    </article>
  );
};

export default Job;
