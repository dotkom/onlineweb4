import React from 'react';
import Tag from './Tag';
import tagsPropTypes from '../propTypes/tags';

const TagList = ({ tags, handleChange, heading }) => (
  <div>
    <h3>{heading}</h3>
    <ul>
      {Object.keys(tags).map(id => (
        <Tag
          key={id}
          changeKey={id}
          selected={tags[id].display}
          handleChange={handleChange}
          title={tags[id].name}
        />
      ))}
    </ul>
  </div>
);

TagList.propTypes = {
  handleChange: React.PropTypes.func,
  heading: React.PropTypes.string,
  tags: tagsPropTypes,
};

export default TagList;
