import Tag from '../components/Tag';

class TagContainer extends React.Component {
  constructor() {
    super();
  }

  render() {
    const self = this;

    let tags = Object.keys(this.props.selectedTags).map(tag => (
      <Tag selected={self.props.selectedTags[tag].display} handleChange={self.props.handleChange} title={self.props.selectedTags[tag].name} />
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
