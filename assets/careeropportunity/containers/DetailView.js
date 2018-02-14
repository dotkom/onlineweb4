import React from 'react';
import InfoBox from '../components/InfoOnOpportunity';
import jobPropTypes from '../propTypes/job';

class DetailView extends React.Component {
  constructor(props) {
    super(props);
  }

  const id = parseInt(props.match.params.id, 10);

  const job = props.jobs.find(j => j.id === id);

  componentDidMount(){
      window.scrollTo(0, 0);
  }

  render() {
    return job ? (
      <InfoBox {...job} />
    ) : (
      <div>Denne karrieremuligheten eksisterer ikke.</div>
    );
  }
}

DetailView.propTypes = {
  jobs: React.PropTypes.arrayOf(React.PropTypes.shape(jobPropTypes)),
  match: React.PropTypes.shape({
    isExact: React.PropTypes.bool,
    params: React.PropTypes.object.isRequired,
    path: React.PropTypes.string.isRequired,
    url: React.PropTypes.string.isRequired,
  }),
};

export default DetailView;
