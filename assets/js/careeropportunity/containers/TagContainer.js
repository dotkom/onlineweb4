import Tag from '../components/Tag';

class TagContainer extends React.Component {
  constructor() {
    super();
  }

  render() {
    let tags = this.props.tags.map(function(tag) {
      return (
        <Tag selected={this.props.selectedTags[tag]} handleChange={this.props.handleChange} title={tag} />
      );
    }.bind(this));

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
