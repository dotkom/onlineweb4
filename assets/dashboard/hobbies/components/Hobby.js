import React from 'react';
import { Link } from 'react-router-dom';
import Urls from 'urls';
import Cookies from 'js-cookie';

import HobbyPropTypes from '../propTypes/hobby';

const deleteHobby = async (id) => {
  try {
    const res = await fetch(`/api/v1/hobbys/${id}`, {
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

const Hobby = ({ hobby }) => {
  const basePath = Urls.hobbies_dashboard_index();
  return (
    <tr>
      <td>{ hobby.title }</td>
      <td>{ hobby.priority }</td>
      <td>{ hobby.active ? 'Ja' : 'Nei' }</td>
      <td className="btn-group">
        <Link
          to={`${basePath}edit/${hobby.id}`}
          type="button"
          className="btn btn-warning"
          title="Rediger"
        >
          <i className="fa fa-pencil" />
        </Link>
        <button
          onClick={() => deleteHobby(hobby.id)}
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

Hobby.propTypes = {
  hobby: HobbyPropTypes,
};

export default Hobby;
