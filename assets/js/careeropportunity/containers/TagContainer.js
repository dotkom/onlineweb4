import Tag from '../components/Tag';

class TagContainer extends React.Component {
  constructor() {
    super();
  }

  render() {
    const self = this;

    let tags = Object.keys(this.props.tags).map(id => (
      <Tag key={id} selected={self.props.tags[id].display} handleChange={self.props.handleChange.bind(self, id)} title={self.props.tags[id].name} />
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
