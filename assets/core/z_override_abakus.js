import './less/z_override_abakus.less';

const hspLogo = require('../../files/static/img/abakus_logo.png');

const overrideWithAbakus = () => {
  // Updating main sponsor logo and text.
  const hspImg = document.querySelector('.ms-img');
  hspImg.src = hspLogo;
  const hspSpan = document.querySelector('.ms-span');
  hspSpan.innerHTML = 'From dotkom with <i class="glyphicon glyphicon-heart"></i>';
};

overrideWithAbakus();
