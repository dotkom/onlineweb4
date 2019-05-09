import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Urls from 'urls';

import DashboardTable from 'dashboard/common/DashboardTable';
import DashboardPanel from 'dashboard/common/DashboardPanel';
import DashboardContainer from 'dashboard/common/DashboardContainer';

import getAllHobbies from '../api/hobby';
import Hobby from '../components/Hobby';

const DEFAULT_HOBBIES = [];

const HobbiesList = () => {
  const basePath = Urls.hobbies_dashboard_index();
  const [hobbies, setHobbies] = useState(DEFAULT_HOBBIES);

  const getHobbies = async () => {
    const newImages = await getAllHobbies();
    setHobbies(newImages);
  };

  useEffect(() => {
    getHobbies();
  }, []);

  return (
    <DashboardContainer>
      <Link to={`${basePath}new`}>
        <p className="btn btn-success">Opprett ny interessegruppe</p>
      </Link>
      <DashboardPanel title="Oversikt">
        <DashboardTable headers={['Tittel', 'Sortingsprioritet', 'Vises på siden', 'Handling']}>
          { hobbies.map(hobby => (
            <Hobby key={hobby.id} hobby={hobby} />
          )) }
        </DashboardTable>
      </DashboardPanel>
    </DashboardContainer>
  );
};

export default HobbiesList;
