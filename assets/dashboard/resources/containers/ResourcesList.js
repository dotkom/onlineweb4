import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Urls from 'urls';

import getAllResources from '../api/resource';
import Resource from '../components/Resource';
import DashboardTable from '../../common/DashboardTable';
import DashboardPanel from '../../common/DashboardPanel';
import DashboardContainer from '../../common/DashboardContainer';

const DEFAULT_RESOURCES = [];

const ResourcesList = () => {
  const basePath = Urls.resources_dashboard_index();
  const [resources, setResources] = useState(DEFAULT_RESOURCES);

  const getResources = async () => {
    const newImages = await getAllResources();
    setResources(newImages);
  };

  useEffect(() => {
    getResources();
  }, []);

  return (
    <DashboardContainer>
      <Link to={`${basePath}new`}>
        <p className="btn btn-success">Opprett ny ressurs</p>
      </Link>
      <DashboardPanel title="Oversikt">
        <DashboardTable headers={['Tittel', 'Sortingsprioritet', 'Vises på siden', 'Handling']}>
          { resources.map(resource => (
            <Resource key={resource.id} resource={resource} />
          )) }
        </DashboardTable>
      </DashboardPanel>
    </DashboardContainer>
  );
};

export default ResourcesList;
