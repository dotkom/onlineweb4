import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import Cookies from 'js-cookie';
import Urls from 'urls';

import HobbyForm from '../components/HobbyForm';
import HobbyDetails from '../components/HobbyDetails';

const DEFAULT_VALUES = {
  title: '',
  description: '',
  read_more_link: '',
  image_id: 0,
  priority: 0,
  active: true,
};

const getHobby = async (id) => {
  try {
    const res = await fetch(`/api/v1/hobbys/${id}/?format=json`, {
      method: 'GET',
    });
    if (res.ok) {
      const json = await res.json();
      return json;
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(err);
    return null;
  }
  return null;
};

const patchHobby = async (id, hobby) => {
  try {
    const res = await fetch(`/api/v1/hobbys/${id}/`, {
      method: 'PATCH',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      body: JSON.stringify(hobby),
    });
    if (res.ok) {
      const json = await res.json();
      return json;
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(err);
    return null;
  }
  return null;
};

const EditHobby = ({ id }) => {
  const [hobby, setHobby] = useState(DEFAULT_VALUES);
  const basePath = Urls.hobbies_dashboard_index();

  const initHobby = async () => {
    const res = await getHobby(id);
    if (res) {
      setHobby({
        ...res,
        image_id: res.image ? res.image.id : null,
      });
    }
  };

  const handleSave = () => {
    patchHobby(id, hobby);
  };

  useEffect(() => {
    initHobby();
  }, []);

  const title = `Endre på interessegruppe${hobby.title ? `n: ${hobby.title}` : ''}`;

  return (
    <HobbyDetails title={title} backUrl={basePath}>
      <HobbyForm
        hobby={hobby}
        setHobby={setHobby}
        onSave={handleSave}
        onCancel={initHobby}
      />
    </HobbyDetails>
  );
};

EditHobby.propTypes = {
  id: PropTypes.string.isRequired,
};

export default EditHobby;
