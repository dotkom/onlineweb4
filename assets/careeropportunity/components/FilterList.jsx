import React from 'react';
import PropTypes from 'prop-types';
import { Col } from 'react-bootstrap';
import TagList from './TagList';
import tagsPropTypes from '../propTypes/tags';
import SearchBox from '../components/SearchBox';

const FilterList = ({ tags, filterText, handleTagChange, handleReset, handleFilterChange }) => (
  <Col xs={12} sm={12} md={3} className="pull-right">
    <div className="filters">
      <SearchBox text={filterText} onChange={e => handleFilterChange(e)} />

      <TagList
        heading="Bedrifter"
        tags={tags.companies}
        handleChange={(tag) => {
          handleTagChange('companies', tag);
        }}
      />

      <TagList
        heading="Typer"
        tags={tags.jobTypes}
        handleChange={(tag) => {
          handleTagChange('jobTypes', tag);
        }}
      />

      <TagList
        heading="Sted"
        tags={tags.locations}
        handleChange={(tag) => {
          handleTagChange('locations', tag);
        }}
      />

      <TagList
        heading="Frist"
        tags={tags.deadlines}
        handleChange={(tag) => {
          handleTagChange('deadlines', tag, true);
        }}
      />

      <button onClick={handleReset}>Reset</button>
    </div>
  </Col>
);

FilterList.propTypes = {
  handleTagChange: PropTypes.func,
  tags: tagsPropTypes,
  handleReset: PropTypes.func,
  handleFilterChange: PropTypes.func.isRequired,
  filterText: PropTypes.string.isRequired,
};

export default FilterList;
