import moment from 'moment';

moment.locale('nb');

class Job extends React.Component {
  constructor() {
    super();
  }

  render() {
    let data = this.props.jobData;

    let locations = data.location.map((location) => location.name).reverse();

    if (locations.length >= 2) {
      locations = `${locations.slice(0, -1).join(', ')} and ${locations[locations.length - 1]}`;
    } else if (locations.length === 0) {
      locations = 'Ikke spesifisert';
    }

    let deadline = data.deadline ? moment(data.deadline).format('Do MMMM YYYY, HH:mm') : 'Ikke spesifisert';

    return (
      <article className="row">
        <div className="col-xs-12 col-md-4">
          <a href="/careeropportunity/4/">
            <picture>
              <source srcset={data.company.image.lg} media="(max-width: 992px)" />
              <img src={data.company.image.md} alt="Firmalogo" />
            </picture>
          </a>
        </div>

        <div className="col-xs-12 col-md-8">
          <h1>
            <a href="/careeropportunity/4/">{data.company.name} - {data.title}</a>
          </h1>

          <div className="ingress">{data.ingress}</div>

          <div className="meta">
            <div className="col-md-4">
              <p>Type: {data.employment.name}</p>
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
  }
}

export default Job;
