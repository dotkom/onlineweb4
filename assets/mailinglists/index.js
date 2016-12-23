import Masonry from 'masonry-layout';
import './less/mailinglists.less';


// Masonry
const container = document.querySelector('#masonry');
const masonry = new Masonry(container, {
  // options
  gutter: 10,
  columnWidth: 260,
  itemSelector: '.mailinglist',
});
setTimeout(() => {
  // If Masonry didn't get it right the first time
  masonry.layout();
}, 1500);
