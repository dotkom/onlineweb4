import React from 'react';
import classNames from 'classnames';

class Tag extends React.Component {
  constructor() {
    super();

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    this.props.handleChange(this.props.changeKey);
  }

  render() {
    const classes = classNames({
      selected: this.props.selected,
    });

    return <li className={classes} onClick={this.handleClick}>{this.props.title}</li>;
  }
}

Tag.propTypes = {
  title: React.PropTypes.string,
  selected: React.PropTypes.bool,
  handleChange: React.PropTypes.func,
  changeKey: React.PropTypes.string,
};

export default Tag;
