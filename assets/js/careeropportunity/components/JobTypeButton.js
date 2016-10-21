class JobTypeButton extends React.Component {
  constructor() {
    super();

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(key) {
    this.props.handleChange(key);
  }

  render() {
    return (
      <button onClick={this.handleClick.bind(this, this.props.jobType)}>{this.props.title} - {this.props.selected ? 'yes' : 'no'}</button>
    );
  }
}

export default JobTypeButton;
