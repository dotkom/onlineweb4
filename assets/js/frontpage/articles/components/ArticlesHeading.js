import React from 'react';
import { Glyphicon } from 'react-bootstrap';

const ArticlesHeading = () => (
  <div className="page-header clearfix">
    <div className="row">
      <div className="col-md-8 col-xs-6">
        <h1 id="articles-heading">Artikler</h1>
      </div>
      <div className="col-md-4 col-xs-6 archive-link">
        <a href="{Urls.article_archive}">ARKIV
          <Glyphicon glyph="chevron-right" />
        </a>
      </div>
    </div>
  </div>
);

export default ArticlesHeading;
