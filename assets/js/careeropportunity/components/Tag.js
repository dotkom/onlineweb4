import classNames from 'classnames';

class Tag extends React.Component {
  constructor() {
    super();

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(key) {
    this.props.handleChange(key);
  }

  render() {
    let classes = classNames({
      'selected': this.props.selected
    });

    return (
      <li className={classes} onClick={this.handleClick.bind(this, this.props.title)}>{this.props.title}</li>
    );
  }
}

export default Tag;
