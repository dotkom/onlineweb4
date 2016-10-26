class Job extends React.Component {
  constructor() {
    super();
  }

  render() {
    return (
      <div className="job">
        {this.props.jobTitle}
      </div>
    );
  }
}

export default Job;
