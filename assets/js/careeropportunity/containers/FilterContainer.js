import TagContainer from './TagContainer';

class FilterContainer extends React.Component {
  constructor(props) {
    super();

    this.handleCompanyChange = this.handleCompanyChange.bind(this);
    this.handleJobTypeChange = this.handleJobTypeChange.bind(this);
    this.handleLocationChange = this.handleLocationChange.bind(this);
    this.handleDeadlineChange = this.handleDeadlineChange.bind(this);
  }

  handleCompanyChange(tag) {
    this.props.handleTagChange('companies', tag);
  }

  handleJobTypeChange(tag) {
    this.props.handleTagChange('jobTypes', tag);
  }

  handleLocationChange(tag) {
    this.props.handleTagChange('locations', tag);
  }

  handleDeadlineChange(tag) {
    this.props.handleTagChange('deadlines', tag, true);
  }

  render() {
    return (
      <div className="col-xs-12 col-sm-12 col-md-3 pull-right">
        <div className="filters">
          <TagContainer heading="Bedrifter" tags={this.props.tags.companies} selectedTags={this.props.selectedTags.companies} handleChange={this.handleCompanyChange} />
          <TagContainer heading="Typer" tags={this.props.tags.jobTypes} selectedTags={this.props.selectedTags.jobTypes} handleChange={this.handleJobTypeChange} />
          <TagContainer heading="Sted" tags={this.props.tags.locations} selectedTags={this.props.selectedTags.locations} handleChange={this.handleLocationChange} />
          <TagContainer heading="Frist" tags={this.props.tags.deadlines} selectedTags={this.props.selectedTags.deadlines} handleChange={this.handleDeadlineChange} />
          <button onClick={this.props.handleReset}>Reset</button>
        </div>
      </div>
    );
  }
}

export default FilterContainer;
