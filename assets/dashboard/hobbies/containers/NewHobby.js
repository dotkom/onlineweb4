import React, { useState } from 'react';
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

const postHobby = async (hobby) => {
  try {
    const res = await fetch('/api/v1/hobbys/', {
      method: 'POST',
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

const NewHobby = () => {
  const [hobby, setHobby] = useState(DEFAULT_VALUES);
  const basePath = Urls.hobbies_dashboard_index();
  return (
    <HobbyDetails title="Lag en ny interessegruppe" backUrl={basePath}>
      <HobbyForm
        hobby={hobby}
        setHobby={setHobby}
        onSave={() => postHobby(hobby)}
        onCancel={() => setHobby(DEFAULT_VALUES)}
      />
    </HobbyDetails>
  );
};

export default NewHobby;
