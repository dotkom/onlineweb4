import jQuery from 'jquery';

/*
    The Company module exposes functionality needed in the company section
    of the dashboard.
*/

const Inventory = (function PrivateInventory($) {
  const postDeleteForm = (url) => {
    $(`<form method="POST" action="${url}">` +
        `<input type="hidden" name="csrfmiddlewaretoken" value="${
        $('input[name=csrfmiddlewaretoken]').val()}"></form>`).submit();
  };

  return {
    // Bind them buttons and other initial functionality here
    init() {
      $('#inventory-delete-item').on('click', function deleteItem(e) {
        e.preventDefault();
        $('.confirm-delete-item').data('id', $(this).data('id'));
      });

      $('.deletebatch').on('click', function deleteBatch(e) {
        e.preventDefault();
        $('.confirm-delete-batch').data('id', $(this).data('id'));
      });

      $('.confirm-delete-item').on('click', function confirmDeleteItem() {
        const url = `/dashboard/inventory/item/${$(this).data('id')}/delete/`;
        postDeleteForm(url);
      });

      $('.confirm-delete-batch').on('click', function confirmDeleteBatch() {
        const itemId = $('#item_id').val();
        const url = `/dashboard/inventory/item/${itemId}/batch/${$(this).data('id')}/delete/`;
        postDeleteForm(url);
      });

      $('#inventory-add-batch').on('click', (e) => {
        e.preventDefault();
        $('#inventory-add-batch-form').slideToggle(200);
      });
    },

  };
}(jQuery));


export default Inventory;
