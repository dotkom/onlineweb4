import React from 'react';
import { Link } from 'react-router-dom';
import Urls from 'urls';
import Cookies from 'js-cookie';

import ResourcePropTypes from '../propTypes/resource';

const deleteResource = async (id) => {
  try {
    const res = await fetch(`/api/v1/resources/${id}`, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
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

const Resource = ({ resource }) => {
  const basePath = Urls.resources_dashboard_index();
  return (
    <tr>
      <td>{ resource.title }</td>
      <td>{ resource.priority }</td>
      <td>{ resource.active ? 'Ja' : 'Nei' }</td>
      <td className="btn-group">
        <Link
          to={`${basePath}edit/${resource.id}`}
          type="button"
          className="btn btn-warning"
          title="Rediger"
        >
          <i className="fa fa-pencil" />
        </Link>
        <button
          onClick={() => deleteResource(resource.id)}
          type="button"
          className="btn btn-danger"
          title="Slett"
        >
          <i className="fa fa-trash" />
        </button>
      </td>
    </tr>
  );
};

Resource.propTypes = {
  resource: ResourcePropTypes,
};

export default Resource;
