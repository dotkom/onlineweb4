class Tag extends React.Component {
  constructor() {
    super();

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(key) {
    this.props.handleChange(key);
  }

  render() {
    return (
      <li onClick={this.handleClick.bind(this, this.props.tagKey)}>{this.props.title} - {this.props.selected ? 'yes' : 'no'}</li>
    );
  }
}

export default Tag;
