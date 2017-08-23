import jQuery from 'jquery';

const WebshopGallery = (function PrivateWebshopGallery($) {
  const images = [];
  let chosenList;

  const updateListImages = () => {
    chosenList.empty();
    for (let i = 0; i < images.length; i += 1) {
      const clone = $(images[i]).clone();
      // Remove on click
      clone.on('click', () => {
        // TODO: Properly fix function orders
        // eslint-disable-next-line no-use-before-define
        removeImage(clone.context);
      });
      chosenList.append(clone);
    }
  };


  const addImage = (image) => {
    const $image = $(image);
    images.push(image);
    updateListImages();
    $image.addClass('image-selected');
  };

  const removeImage = (image) => {
    const $image = $(image);
        // Remove from list
    const index = images.indexOf(image);
    if (index > -1) {
      images.splice(index, 1);
    }
    updateListImages();
    $image.removeClass('image-selected');
  };

  const toggleImage = (image) => {
    const $image = $(image); // we php now
    const selected = $image.hasClass('image-selected');
    if (!selected) {
      addImage(image);
    } else {
      removeImage(image);
    }
  };

  return {
    init() {
      chosenList = $('#webshop-chosen-list');
      $('#webshop-image-list').on('click', 'img', function clickImage(e) {
        e.preventDefault();
        toggleImage(this);
      });
      chosenList.on('click', 'img', function clickChosen(e) {
        e.preventDefault();
        removeImage(this);
      });
    },
  };
}(jQuery));

export default WebshopGallery;
