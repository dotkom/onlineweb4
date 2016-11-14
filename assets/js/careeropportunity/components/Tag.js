import classNames from 'classnames';

const Tag = ({ title, selected, handleChange }) => {
  let classes = classNames({
    'selected': selected,
  });

  return <li className={classes} onClick={handleChange.bind(this, title)}>{title}</li>;
};

export default Tag;
