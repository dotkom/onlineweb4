import React from 'react';
import PropTypes from 'prop-types';

import BooleanInput from '../../common/forms/BooleanInput';
import TextInput from '../../common/forms/TextInput';
import NumberInput from '../../common/forms/NumberInput';
import ResourcePropTypes from '../propTypes/resource';
import TextArea from '../../common/forms/TextArea';
import ResponsiveImageInput from '../../common/forms/ResponseiveImageInput';

const ResourceForm = ({ resource, setResource, onSave, onCancel }) => {
  const onInput = (name, value) => {
    setResource(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <form onSubmit={event => event.preventDefault()}>
      <TextInput
        name="title"
        onChange={onInput}
        value={resource.title}
        label="Tittel"
        placeholder="Gi en enkel tittel på ressursen"
        required
      />
      <br />
      <TextArea
        name="description"
        onChange={onInput}
        value={resource.description}
        label="Beskrivelse"
        placeholder="Beskriv ressursen med Markdown. Legg ved lenker på bunnen"
        required
      />
      <br />
      <NumberInput
        name="priority"
        onChange={onInput}
        value={resource.priority}
        label="Prioritet"
        placeholder="Prioriteten brukes for å bestemme rekkefølge på listen av ressurser"
        required
      />
      <br />
      <ResponsiveImageInput
        name="image_id"
        onChange={onInput}
        value={resource.image_id}
        label="Bilde"
        initialQuery={resource.image ? resource.image.name : undefined}
        required
      />
      <br />
      <BooleanInput
        name="active"
        onChange={onInput}
        value={resource.active}
        label="Vis ressursen i listen"
        required
      />
      <br />
      <div className="btn-group">
        <button onClick={onSave} type="submit" className="btn btn-success">Lagre</button>
        <button onClick={onCancel} className="btn btn-danger">Avbryt</button>
      </div>
    </form>
  );
};

ResourceForm.propTypes = {
  onSave: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  setResource: PropTypes.func.isRequired,
  resource: ResourcePropTypes.isRequired,
};

export default ResourceForm;
