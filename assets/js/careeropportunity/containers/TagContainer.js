import Tag from '../components/Tag';

class TagContainer extends React.Component {
  constructor() {
    super();
  }

  render() {
    const self = this;

    let tags = Object.keys(this.props.selectedTags).map(id => (
      <Tag key={id} selected={self.props.selectedTags[id].display} handleChange={self.props.handleChange.bind(self, id)} title={self.props.selectedTags[id].name} />
    ));

    return (
      <div>
        <h3>{this.props.heading}</h3>
        <ul>
          {tags}
        </ul>
      </div>
    );
  }
}

export default TagContainer;
