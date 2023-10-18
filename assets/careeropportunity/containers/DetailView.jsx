import React from 'react';
import PropTypes from 'prop-types';
import InfoBox from '../components/InfoOnOpportunity';
import jobPropTypes from '../propTypes/job';

class DetailView extends React.Component {
  constructor(props) {
    super(props);
    this.id = parseInt(props.match.params.id, 10);
    this.job = props.jobs.find(j => j.id === this.id);
  }

  componentDidMount() {
    window.scrollTo(0, 0);
  }

  componentWillReceiveProps(nextProps) {
    this.id = parseInt(nextProps.match.params.id, 10);
    this.job = nextProps.jobs.find(j => j.id === this.id);
  }

  render() {
    return this.job ? (
      <InfoBox {...this.job} />
    ) : (
      <div>Denne karrieremuligheten eksisterer ikke.</div>
    );
  }
}

DetailView.propTypes = {
  jobs: PropTypes.arrayOf(PropTypes.shape(jobPropTypes)),
  match: PropTypes.shape({
    isExact: PropTypes.bool,
    params: PropTypes.object.isRequired,
    path: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
  }),
};

export default DetailView;
