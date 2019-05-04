import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
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

const getResource = async (id) => {
  try {
    const res = await fetch(`/api/v1/resources/${id}/?format=json`, {
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

const patchResource = async (id, resource) => {
  try {
    const res = await fetch(`/api/v1/resources/${id}/`, {
      method: 'PATCH',
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

const EditResource = ({ id }) => {
  const [resource, setResource] = useState(DEFAULT_VALUES);
  const basePath = Urls.resources_dashboard_index();

  const initResource = async () => {
    const res = await getResource(id);
    if (res) {
      setResource({
        ...res,
        image_id: res.image.id,
      });
    }
  };

  const handleSave = () => {
    patchResource(id, resource);
  };

  useEffect(() => {
    initResource();
  }, []);

  return (
    <ResourceDetails title="Lag en ny ressurs" backUrl={basePath}>
      <ResourceForm
        resource={resource}
        setResource={setResource}
        onSave={handleSave}
        onCancel={initResource}
      />
    </ResourceDetails>
  );
};

EditResource.propTypes = {
  id: PropTypes.string.isRequired,
};

export default EditResource;
