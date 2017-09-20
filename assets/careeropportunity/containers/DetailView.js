import React from 'react';
import moment from 'moment';
import { Grid, Col, Row } from 'react-bootstrap';
import FilterList from '../components/FilterList';
import JobList from '../components/JobList';
import InfoBox from '../components/InfoOnOpportunity';

class DetailView extends React.Component {
    constructor(props){
        super(props);
    }
    render(){
      const { job }=this.props;
        return (
          <InfoBox deadline={job}/>
        );
    }
}

export default DetailView
