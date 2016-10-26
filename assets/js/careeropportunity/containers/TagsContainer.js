import Tag from '../components/Tag';

class TagsContainer extends React.Component {
  constructor(props) {
    super();

    this.state = {
      selectedTags: {}
    };

    for (let key in props.tags) {
      if (props.tags.hasOwnProperty(key)) {
        this.state.selectedTags[key] = false;
      }
    }

    // Store a copy of the initial store for use with resetting.
    this.initialState = Object.assign({}, this.state)

    this.handleChange = this.handleChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
  }

  // Handles a Tag-component being clicked.
  handleChange(selectedKey) {
    let selectedTags = this.state.selectedTags;

    selectedTags[selectedKey] = !selectedTags[selectedKey];

    this.setState({
      selectedTags: selectedTags
    });

    this.props.handleChange(selectedTags);
  }

  // Reset all buttons to their initial state.
  handleReset() {
    this.setState(this.initialState);
    this.props.handleChange(resetTags);
  }

  render() {
    let tags = this.props.tags.map(function(tag) {
      return (
        <Tag selected={this.state.selectedTags[tag.key]} tagKey={tag.key} handleChange={this.handleChange} title={tag.title} />
      );
    }.bind(this));

    return (
      <ul>
        {tags}
        <button onClick={this.handleReset}>reset</button>
      </ul>
    );
  }
}

export default TagsContainer;
