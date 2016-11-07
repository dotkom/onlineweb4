import TagContainer from './TagContainer';

class FilterContainer extends React.Component {
  constructor(props) {
    super();

    this.handleCompanyChange = this.handleCompanyChange.bind(this);
    this.handleJobTypeChange = this.handleJobTypeChange.bind(this);
    this.handleLocationChange = this.handleLocationChange.bind(this);
  }

  handleCompanyChange(updatedValues) {
    this.props.handleTagChange('company', updatedValues);
  }

  handleJobTypeChange(updatedValues) {
    this.props.handleTagChange('jobType', updatedValues);
  }

  handleLocationChange(updatedValues) {
    this.props.handleTagChange('location', updatedValues);
  }

  render() {
    return (
      <div className="col-xs-12 col-sm-12 col-md-3 pull-right">
        <div className="filters">
          <TagContainer heading="Bedrifter" tags={this.props.tags.companies} handleChange={this.handleCompanyChange} />
          <TagContainer heading="Typer" tags={this.props.tags.jobTypes} handleChange={this.handleJobTypeChange} />
          <TagContainer heading="Sted" tags={this.props.tags.locations} handleChange={this.handleLocationChange} />
        </div>
      </div>
    );
  }
}

export default FilterContainer;
