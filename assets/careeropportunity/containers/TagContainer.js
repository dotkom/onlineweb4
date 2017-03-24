import React from 'react';
import Tag from '../components/Tag';

const TagContainer = ({ tags, handleChange, heading }) => {
  const tagElems = Object.keys(tags).map(id => (
    <Tag
      key={id}
      changeKey={id}
      selected={tags[id].display}
      handleChange={handleChange}
      title={tags[id].name}
    />
  ));

  return (
    <div>
      <h3>{heading}</h3>
      <ul>
        {tagElems}
      </ul>
    </div>
  );
};

TagContainer.propTypes = {
  handleChange: React.PropTypes.func,
  heading: React.PropTypes.string,
  tags: React.PropTypes.object,
};

export default TagContainer;
