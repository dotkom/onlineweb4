import $ from 'jquery';

const postDeleteForm = (url) => {
  $(`<form method="POST" action="${url}">` +
      `<input type="hidden" name="csrfmiddlewaretoken" value="${
      $('input[name=csrfmiddlewaretoken]').val()}"></form>`).submit();
};

const init = () => {
  $('#webshop-delete-product').on('click', function deleteProduct(e) {
    e.preventDefault();
    $('.confirm-delete-product').data('slug', $(this).data('slug'));
  });

  $('.confirm-delete-product').on('click', function confirmDeleteProduct() {
    const url = `/dashboard/webshop/product/${$(this).data('slug')}/delete`;
    postDeleteForm(url);
  });

  $('#webshop-delete-category').on('click', function deleteCategory(e) {
    e.preventDefault();
    $('.confirm-delete-category').data('slug', $(this).data('slug'));
  });

  $('.confirm-delete-category').on('click', function confirmDeleteCategory() {
    const url = `/dashboard/webshop/category/${$(this).data('slug')}/delete`;
    postDeleteForm(url);
  });
};

export default {
  init,
};
