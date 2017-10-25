import React from 'react';
import Markdown from 'react-markdown';
import { formatLocations } from './Job';

const InfoBox = ({
  title,
  description,
  companyId,
  locations,
  deadline,
  type,
  companyName,
  companyDescription,
  companyImage }) => (
  <section id="careeropportunity">
    <div className="container">
      <div className="row">
        <div className="col-md-12">
          <div className="page-header">
            <h2>{title}</h2>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-8 col-sm-7 careerdescription">
          <Markdown
            source={description}
            escapeHtml={true}
          />
        </div>

        <div className="col-md-4 col-sm-5">
          <div className="row">
            <div className="col-md-12">
            <a href={'/company/' + companyId}>
                <picture>
                  <source srcSet={companyImage.lg} media="(max-width: 992px)" />
                  <img src={companyImage.md} width="100%" />
                </picture>
              </a> 
            </div>
          </div>

          <div className="company">
            <a href={'/company/' + companyId}>
              <div className="row">
                <div className="col-md-12">
                  <h3>{companyName}</h3>
                </div>
              </div>

              <div className="row">
                <div className="col-md-12">
                  <div className="company-ingress">
                    <Markdown
                      source={companyDescription}
                      escapeHtml={true}
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
                <p>Type: {type}</p>
                <p>Sted: {formatLocations(locations)}</p>
                <p>Frist: {deadline}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

export default InfoBox;