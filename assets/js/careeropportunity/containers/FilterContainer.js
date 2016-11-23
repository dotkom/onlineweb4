import TagContainer from './TagContainer';
import {Col} from 'react-bootstrap';

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
      <Col xs={12} sm={12} md={3} className="pull-right">
        <div className="filters">
          <TagContainer heading="Bedrifter" tags={this.props.tags.companies} handleChange={this.handleCompanyChange} />
          <TagContainer heading="Typer" tags={this.props.tags.jobTypes} handleChange={this.handleJobTypeChange} />
          <TagContainer heading="Sted" tags={this.props.tags.locations} handleChange={this.handleLocationChange} />
          <TagContainer heading="Frist" tags={this.props.tags.deadlines} handleChange={this.handleDeadlineChange} />
          <button onClick={this.props.handleReset}>Reset</button>
        </div>
      </Col>
    );
  }
}

export default FilterContainer;
