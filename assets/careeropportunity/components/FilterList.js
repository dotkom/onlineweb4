import React from 'react';
import { Col } from 'react-bootstrap';
import TagList from './TagList';
import tagsPropTypes from '../propTypes/tags';

const FilterList = ({ tags, handleTagChange, handleReset }) => (
  <Col xs={12} sm={12} md={3} className="pull-right">
    <div className="filters">
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
  handleTagChange: React.PropTypes.func,
  tags: tagsPropTypes,
  handleReset: React.PropTypes.func,
};

export default FilterList;
