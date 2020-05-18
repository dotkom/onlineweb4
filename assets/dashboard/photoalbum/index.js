import Urls from 'urls';
import $ from 'jquery';
import { plainUserTypeahead } from 'common/typeahead';
import Cookies from 'js-cookie';

const httpRequest = async (url, method, data) => {
  try {
    const res = await fetch(url, {
      method,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      body: JSON.stringify(data),
    });
    if (res.ok && !(res.status === 204)) {
      const json = await res.json();
      return json;
    }
  } catch (err) {
    return null;
  }
  return null;
};

const createTag = async (userId, photoId) => {
  const url = Urls['album_tags-list']();
  return await httpRequest(url, 'POST', { user: userId, photo: photoId });
};

const deleteTag = async (tagId) => {
  const url = Urls['album_tags-detail'](tagId);
  return await httpRequest(url, 'DELETE');
};

const registerDeleteTagButton = (button) => {
  button.addEventListener('click', async (event) => {
    event.preventDefault();
    await deleteTag(button.dataset.tagpk);
    button.remove();
  });
};

const renderNewTag = (tagId, name) => {
  const tagList = document.querySelector('#tag-data');
  const tagButton = document.createElement('button');
  tagButton.className = 'btn btn-default delete-tag-button';
  tagButton.dataset.tagpk = tagId;
  tagButton.innerText = name;
  tagList.appendChild(tagButton);
  registerDeleteTagButton(tagButton);
};

const postDeleteForm = (url) => {
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = url;

  const crsfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
  const crsfTokenInput = document.createElement('input');
  crsfTokenInput.type = 'hidden';
  crsfTokenInput.name = 'csrfmiddlewaretoken';
  crsfTokenInput.value = crsfToken;

  form.appendChild(crsfTokenInput);
  form.submit();

  const body = document.querySelector('body');
  body.appendChild(form);
  form.submit();
  body.removeChild(form);
};

const reverseUrl = (reverse, ...args) => Urls[reverse](...args);

const init = () => {
  const deletePhotoButton = document.querySelector('#photoalbum-delete-photo');
  const deletePhotoConfirm = document.querySelector('.confirm-delete-photo');

  if (deletePhotoConfirm) {
    deletePhotoConfirm.addEventListener('click', () => {
      const url = reverseUrl(
        'dashboard-photoalbum:photo_delete',
        deletePhotoButton.dataset.pk);
      postDeleteForm(url);
    });
  }

  const deleteAlbumButton = document.querySelector('#photoalbum-delete-album');
  const deleteAlbumConfirm = document.querySelector('.confirm-delete-album');

  if (deleteAlbumConfirm) {
    deleteAlbumConfirm.addEventListener('click', () => {
      const url = reverseUrl(
        'dashboard-photoalbum:album_delete',
        deleteAlbumButton.dataset.pk);
      postDeleteForm(url);
    });
  }

  /* Typeahead for user search */
  plainUserTypeahead($('#usersearch'), async (e, datum) => {
    const tagData = document.querySelector('#tag-data').dataset;
    document.querySelector('#usersearch').value = '';
    const searchInput = document.querySelector('#usersearch');
    searchInput.value = '';
    const data = await createTag(datum.id, tagData.photopk);
    if (data) {
      renderNewTag(data.id, datum.value);
    }
  });

  document.querySelectorAll('.delete-tag-button').forEach(registerDeleteTagButton);
};

document.addEventListener('DOMContentLoaded', init);
