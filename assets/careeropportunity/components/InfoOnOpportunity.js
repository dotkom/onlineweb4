import React from 'react';
import PropTypes from 'prop-types';
import Markdown from 'react-markdown';
import { formatLocations } from './Job';
import companyImageProps from '../propTypes/companyImage';

const InfoBox = props => (
  <section id="careeropportunity">
    <div className="container">
      <div className="row">
        <div className="col-md-12">
          <div className="page-header">
            <h2>{props.title}</h2>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-8 col-sm-7 careerdescription">
          <Markdown
            source={props.description}
            escapeHtml
          />
        </div>

        <div className="col-md-4 col-sm-5">
          <div className="row">
            <div className="col-md-12">
              <a href={`/company/${props.companyId}`}>
                <picture>
                  <source srcSet={props.companyImage.lg} media="(max-width: 992px)" />
                  <img src={props.companyImage.md} width="100%" alt={props.companyName} />
                </picture>
              </a>
            </div>
          </div>

          <div className="company">
            <a href={`/company/${props.companyId}`}>
              <div className="row">
                <div className="col-md-12">
                  <h3>{props.companyName}</h3>
                </div>
              </div>

              <div className="row">
                <div className="col-md-12">
                  <div className="company-ingress">
                    <Markdown
                      source={props.companyDescription}
                      escapeHtml
                    />
                  </div>

                  <p className="pull-right company-image-caption">Trykk for mer info</p>
                </div>
              </div>
            </a>
          </div>

          <div className="company">
            <div className="row">
              <div className="col-md-12">
                <h3>Nøkkelinformasjon</h3>
              </div>
            </div>

            <div className="row">
              <div className="col-md-12">
                <p>Type: {props.type}</p>
                <p>Sted: {formatLocations(props.locations)}</p>
                <p>Frist: {props.deadline}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

InfoBox.propTypes = {
  title: PropTypes.string,
  deadline: PropTypes.string,
  locations: PropTypes.arrayOf(PropTypes.string),
  companyId: PropTypes.number,
  description: PropTypes.string,
  type: PropTypes.string,
  companyName: PropTypes.string,
  companyDescription: PropTypes.string,
  companyImage: companyImageProps,
};

export default InfoBox;
