import React from 'react';
import InfoBox from '../components/InfoOnOpportunity';

const DetailView = (props) => {
  const id = parseInt(props.match.params.id, 10);

  const job = props.jobs.find(job => job.id === id);

  return (
    <InfoBox {...job} />
  );
};

export default DetailView;