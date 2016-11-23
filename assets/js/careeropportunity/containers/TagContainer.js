import Tag from '../components/Tag';

const TagContainer = ({ tags, handleChange, heading }) => {
  let tagElems = Object.keys(tags).map(id => (
    <Tag key={id} selected={tags[id].display} handleChange={handleChange.bind(self, id)} title={tags[id].name} />
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

export default TagContainer;
