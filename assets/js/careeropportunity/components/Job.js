class Job extends React.Component {
  constructor() {
    super();
  }

  render() {
    return (
      <article>{this.props.jobTitle}</article>
    );
  }
}

export default Job;
