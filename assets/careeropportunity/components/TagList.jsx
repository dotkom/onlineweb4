import React from 'react';
import PropTypes from 'prop-types';
import Tag from './Tag';
import tagsPropTypes from '../propTypes/tags';

const TagList = ({ tags, handleChange, heading }) => (
  <div>
    <h3>{heading}</h3>
    <div className="TagContainer">
      {Object.keys(tags).map(id => (
        <Tag
          key={id}
          changeKey={id}
          selected={tags[id].display}
          handleChange={handleChange}
          title={tags[id].name}
        />
      ))}
    </div>
  </div>
);

TagList.propTypes = {
  handleChange: PropTypes.func,
  heading: PropTypes.string,
  tags: tagsPropTypes,
};

export default TagList;
