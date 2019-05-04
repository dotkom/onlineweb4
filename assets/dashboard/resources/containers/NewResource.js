import React, { useState } from 'react';
import Cookies from 'js-cookie';
import Urls from 'urls';

import ResourceForm from '../components/ResourceForm';
import ResourceDetails from '../components/ResourceDetails';

const DEFAULT_VALUES = {
  title: '',
  description: '',
  image_id: 0,
  priority: 0,
  active: true,
};

const postResource = async (resource) => {
  try {
    const res = await fetch('/api/v1/resources/', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      body: JSON.stringify(resource),
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

const NewResource = () => {
  const [resource, setResource] = useState(DEFAULT_VALUES);
  const basePath = Urls.resources_dashboard_index();
  return (
    <ResourceDetails title="Lag en ny ressurs" backUrl={basePath}>
      <ResourceForm
        resource={resource}
        setResource={setResource}
        onSave={() => postResource(resource)}
        onCancel={() => setResource(DEFAULT_VALUES)}
      />
    </ResourceDetails>
  );
};

export default NewResource;
