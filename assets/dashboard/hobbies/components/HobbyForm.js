import React from 'react';
import PropTypes from 'prop-types';

import BooleanInput from 'dashboard/common/forms/BooleanInput';
import TextInput from 'dashboard/common/forms/TextInput';
import NumberInput from 'dashboard/common/forms/NumberInput';
import TextArea from 'dashboard/common/forms/TextArea';
import ResponsiveImageInput from 'dashboard/common/forms/ResponseiveImageInput';

import HobbyPropTypes from '../propTypes/hobby';

const HobbyForm = ({ hobby, setHobby, onSave, onCancel }) => {
  const onInput = (name, value) => {
    setHobby(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <form onSubmit={event => event.preventDefault()}>
      <TextInput
        name="title"
        onChange={onInput}
        value={hobby.title}
        label="Navn"
        placeholder="Navnet til interessegruppen"
        required
      />
      <br />
      <TextArea
        name="description"
        onChange={onInput}
        value={hobby.description}
        label="Beskrivelse"
        placeholder="Beskriv interessegruppen med Markdown. Legg ved lenker på bunnen"
        required
      />
      <br />
      <NumberInput
        name="priority"
        onChange={onInput}
        value={hobby.priority}
        label="Prioritet"
        placeholder="Prioriteten brukes for å bestemme rekkefølge på listen av interessegrupper"
        required
      />
      <br />
      <TextInput
        name="read_more_link"
        onChange={onInput}
        value={hobby.read_more_link}
        label="Lenke til informasjon"
        placeholder="Legg inn lenken som fører til mer informasjon om interessegruppen"
        required
      />
      <br />
      <ResponsiveImageInput
        name="image_id"
        onChange={onInput}
        value={hobby.image_id}
        label="Bilde"
        initialQuery={hobby.image ? hobby.image.name : undefined}
        required
      />
      <br />
      <BooleanInput
        name="active"
        onChange={onInput}
        value={hobby.active}
        label="Gjør gruppen synlig"
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

HobbyForm.propTypes = {
  onSave: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  setHobby: PropTypes.func.isRequired,
  hobby: HobbyPropTypes.isRequired,
};

export default HobbyForm;
