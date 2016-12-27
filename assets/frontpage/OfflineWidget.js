import $ from 'jquery';

function OfflineWidget(Utils) {
  const that = $(this);
  this.data = {};
    /* Render the widget */
  OfflineWidget.prototype.render = () => {
    Utils.makeApiRequest({
      url: '/api/v1/offline/?format=json',
      method: 'GET',
      data: {},
      success(data) {
        that.data = data;
        OfflineWidget.prototype.createDom();
      },
    });
  };

    /* Create the DOM */
  OfflineWidget.prototype.createDom = () => {
    const data = that.data;
    const offlines = data.results;
    const prefix = $('#offlineCarousel').data('prefix');
    const suffix = '.thumb.png';
    const itemWrapperStart = '<div class="item centered">';
    const itemWrapperEnd = '</div>';
    let insertMe = '';
    const maxWidth = $('#offlineCarousel .carousel-inner').width();
    const maxWidthPer = 156;
    const issuesPerSlide = Math.floor(maxWidth / maxWidthPer);

    if (offlines.length <= 0) {
            // No issues added
      insertMe += '<p>Ingen utgaver funnet.</p>';
    } else {
            // Create DOM for issues.
      for (let i = 0; i < offlines.length; i += 1) {
        if (i === 0) {
          insertMe += itemWrapperStart;
        }
        insertMe += `<a href="${prefix}${offlines[i].issue}"><img src="${prefix}${offlines[i].issue}${suffix}" /></a>`;

        if (i === offlines.length - 1 || (i + 1) % issuesPerSlide === 0) {
          insertMe += itemWrapperEnd;
          if (i !== offlines.length - 1) {
            insertMe += itemWrapperStart;
          }
        }
      }
    }

    $('#offlineCarousel .carousel-inner').html(insertMe);
    $('#offlineCarousel .carousel-inner div.item:first').addClass('active');
    $('#offlineCarousel').carousel({ interval: false });
  };

    // Recreate DOM on resize
  $(window).on('debouncedresize', () => {
    OfflineWidget.prototype.createDom();
  });
}

export default OfflineWidget;
