class Job extends React.Component {
  constructor() {
    super();
  }

  render() {
    let data = this.props.jobData;

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
              <p>Sted: {data.location.map((location) => location.name).join(', ')}</p>
            </div>

            <div className="col-md-4">
              <p>Frist: {data.deadline || 'Ikke spesifisert'}</p>
            </div>
          </div>
        </div>
      </article>
    );
  }
}

export default Job;
