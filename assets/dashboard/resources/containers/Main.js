import React, { useEffect, useState } from 'react';

import getResponsiveImages from '../api/image';

const Main = () => {
  const [images, setImages] = useState([]);

  const getImages = async () => {
    const newImages = await getResponsiveImages({});
    setImages(newImages);
  };

  useEffect(() => {
    getImages();
  }, []);

  return (
    <div>
      { images.map(image => image.name) }
    </div>
  );
};

export default Main;
