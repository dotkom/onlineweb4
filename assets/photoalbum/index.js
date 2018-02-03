import $ from 'jquery'

import './less/photoalbum.less'

$(document).ready(() => {
  console.log('Running script')
  $('.photo_edit').click(function choose_photo (e) {
		const photo = $(this)
		photo.toggleClass('chosen')
  })

  $('#show_report_photo_form').click(function show_form (e) {
	console.log("Changing visibility")
		const button = $(this)
		//button.style["visibility"] = "hidden"
		document.getElementById('report_photo_form').style["visibility"] = "visible"
  })

  function show_form(e) {
  	console.log("Running show form")
  }

})



