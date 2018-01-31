import $ from 'jquery'

import './less/photoalbum.less'

$(() => {
  console.log('Running script')
  $('.photo_edit').click(function choose_photo (e) {
	  const photo = $(this)
	  photo.toggleClass('chosen')
  })
})
