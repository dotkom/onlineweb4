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

    this.handleChange = this.handleChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
  }

  handleChange(selectedKey) {
    let selectedTags = this.state.selectedTags;

    selectedTags[selectedKey] = !selectedTags[selectedKey];

    this.setState({
      selectedTags: selectedTags
    });

    this.props.handleJobTypeChange(selectedTags);
  }

  handleReset() {
    let resetTagss = {};

    for (let key in this.state.selectedTags) {
      if (this.state.selectedTags.hasOwnProperty(key)) {
        resetTagss[key] = false;
      }
    }

    this.setState({
      selectedTags: resetTagss
    });

    this.props.handleTagsChange(resetTagss);
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
