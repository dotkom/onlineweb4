import $ from 'jquery'

$(document).ready(() => {
  console.log("Running second script")
  $(".photo .big").bind("keydown", function(e) {
    if (e.keyCode == 37) { // Left
      console.log("Left arrow")
    }
    if (e.keyCode == 39) { // Right arrow
      console.log("Right arrow")
    }
  })
})