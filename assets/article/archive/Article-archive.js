import $ from 'jquery';
import Utils from 'common/utils/Utils';
import ArticleArchiveWidget from './ArticleArchiveWidget';

const utils = new Utils(); // Class for the Widget
let isLoadingNewContent = false; // Indicating if we are currently loading something
let page = 1; // What page we are on
const months = {
  januar: 1,
  februar: 2,
  mars: 3,
  april: 4,
  mai: 5,
  juni: 6,
  juli: 7,
  august: 8,
  september: 9,
  oktober: 10,
  november: 11,
  desember: 12,
};
// Object that holds the settings we are building an query from
const articleSettings = {
  archive: true,
  year: null,
  month: null,
  tag: null,
  tagPage: 1,
};

const articleWidget = new ArticleArchiveWidget(utils);

// The initial rendgering (loading from ajax)
// Build settings by url
const pathname = window.location.pathname;
const url = pathname.split('/');
if (url[url.length - 2] === 'month') {
  articleSettings.month = url[url.length - 1];
  articleSettings.year = url[url.length - 3];
} else if (url[url.length - 2] === 'year') {
  articleSettings.year = url[url.length - 1];
} else if (url[url.length - 3] === 'tag') {
  articleSettings.tag = url[url.length - 2];
}
articleWidget.render(1, false, articleSettings);

//
// Method for infinite scrolling
//
$(document).on('scroll', () => {
  // If we are 10px from the bottom, execute new render
  if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
    // Checking to see if we are curently buzy
    if (!isLoadingNewContent) {
      // Set buzy to true so we don't load multiple articles at once
      isLoadingNewContent = true;

      // Increasing page
      page += 1;

      // Do the actuall call with supplied callback
      articleWidget.render(page, false, articleSettings, () => {
        // Setting loading to false, so we can load another round later
        isLoadingNewContent = false;
        if (articleSettings.tag) {
          articleSettings.tagPage += 1;
        }
      });
    }
  }
});

//
// Filtering articles on year (and perhaps month)
//
$('#article_archive_filter a').on('click', function filterArticle(e) {
  // We don't want to redirect!!
  if (e.preventDefault) { e.preventDefault(); } else { e.stop(); }

  // Checking to see if buzy
  if (!isLoadingNewContent) {
    // Set buzy to true so we don't load multiple articles at once
    isLoadingNewContent = true;

    const $obj = $(this);

    // Setting page to 1 again
    page = 1;

    // Updating the settings
    articleSettings.tag = null;
    if ($obj.data('year') !== '' && typeof $obj.data('year') !== 'undefined') {
      articleSettings.year = $obj.data('year');
    } else {
      articleSettings.year = null;
    }
    if ($obj.data('month') !== '' && typeof $obj.data('month') !== 'undefined') {
      articleSettings.month = months[$obj.data('month').toLowerCase()];
    } else {
      articleSettings.month = null;
    }

    articleWidget.render(1, true, articleSettings, () => {
      // Setting loading to false, so we can load another round later
      isLoadingNewContent = false;
    });
  }
});

//
// Filtering articles on tags
//
$('#article_archive_tagcloud a').on('click', function filterTag(e) {
  if (e.preventDefault) {
    e.preventDefault();
  } else {
    e.stop();
  }

  // Set buzy to true so we don't load multiple articles at once
  isLoadingNewContent = true;

  const $obj = $(this);

  // Getting the tag-slug (had to be done using the url…
  const tagUrl = $obj.attr('href').split('/');

  // Updating the settings
  articleSettings.year = null;
  articleSettings.month = null;
  articleSettings.tag = tagUrl[tagUrl.length - 2];
  articleSettings.tagPage = 1;


  page = 1;

  // Render!
  articleWidget.render(1, true, articleSettings, () => {
    // Setting loading to false, so we can load another round later
    isLoadingNewContent = false;
    articleSettings.tagPage += 1;
  });
});

//
// Resetting tag-filter
//
$('#article_archive_filter_reset').on('click', (e) => {
  if (e.preventDefault) { e.preventDefault(); } else {
    e.stop();
  }

  // Set buzy to true so we don't load multiple articles at once
  isLoadingNewContent = true;

  // Updating the settings
  articleSettings.year = null;
  articleSettings.month = null;
  articleSettings.tag = null;
  articleSettings.tagPage = 1;
  page = 1;


  // Render!
  articleWidget.render(1, true, articleSettings, () => {
    // Setting loading to false, so we can load another round later
    isLoadingNewContent = false;
  });
});
