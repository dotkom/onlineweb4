import React from 'react';
import { Grid, Col, Row } from 'react-bootstrap';
import FilterList from '../components/FilterList';
import JobList from '../components/JobList';

const FilterableJobList = (props) => (
  <Grid>
    <Row>
      <Col md={4}>
        <div className="page-header">
          <h2>KARRIEREMULIGHETER</h2>
        </div>
      </Col>
    </Row>

    <Row>
      <FilterList
        tags={props.tags}
        handleTagChange={(type, changedTag, switchMode) => props.handleTagChange(type, changedTag, switchMode)}
        handleReset={() => props.handleReset()}
        handleFilterChange={e => props.handleFilterChange(e)}
        filterText={props.filterText}
      />

      <JobList
        jobs={props.jobs}
        tags={props.tags}
        filterText={props.filterText}
      />
    </Row>
  </Grid>
);

export default FilterableJobList;
