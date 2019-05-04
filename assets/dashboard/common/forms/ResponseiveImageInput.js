import React, { useEffect, useState, Fragment } from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import Field from './Field';
import getResponsiveImages from '../../resources/api/image';

const DEFAULT_IMAGE_PLACEHOLDER = 'Søk på bilder. Du kan bruke titler, tags og beskrivelse';

const ResponsiveImageInput = ({
  name,
  value,
  label,
  onChange,
  required,
  placeholder = DEFAULT_IMAGE_PLACEHOLDER,
  initialQuery,
}) => {
  const [images, setImages] = useState([]);
  const [searchString, setSearchString] = useState('');

  const handleImageClick = id => onChange(name, Number(id));

  const getImages = async (query) => {
    const newImages = await getResponsiveImages({ query });
    setImages(newImages || []);
  };

  const onSearch = () => getImages(searchString);

  const handleQueryChange = event => setSearchString(event.target.value);

  useEffect(() => {
    if (initialQuery) {
      getImages(initialQuery);
    }
  }, [initialQuery]);

  return (
    <Field name={name} label={label} required={required}>
      <Fragment>
        <div className="input-group">
          <input
            id={name}
            value={searchString}
            type="text"
            className="form-control"
            placeholder={placeholder}
            onChange={handleQueryChange}
          />
          <span className="input-group-btn">
            <button className="btn btn-primary" onClick={onSearch}>Søk!</button>
          </span>
        </div>
        { images && images.length !== 0 ?
          <div className="row">
            <hr />
            { images.map(image => (
              <div className="col-md-6 col-sm-12 col-xs-12" key={image.id}>
                <button
                  className={classNames('image-selection-thumbnail',
                  { 'image-selection-thumbnail-active': value === image.id })}
                  onClick={() => handleImageClick(image.id)}
                >
                  <div className="image-selection-thumbnail-image">
                    <img src={image.sm} alt={image.title} title={image.title} />
                  </div>
                  <div className="image-selection-thumbnail-text">
                    <h4 className="image-title">{image.title}</h4>
                    <span className="image-timestamp">{image.timestamp}</span>
                    <p className="image-description">{image.description}</p>
                  </div>
                </button>
              </div>
            )) }
          </div>
        : null }
      </Fragment>
    </Field>
  );
};

ResponsiveImageInput.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
  label: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
  initialQuery: PropTypes.string,
};

export default ResponsiveImageInput;
