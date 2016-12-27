import moment from 'moment';
import $ from 'jquery';
import { makeApiRequest } from 'common/utils';

function ArticleArchiveWidget() {
  // True if we have more elements, false if not. To avoid many empty ajax-calls
  let isMoreElements = true;
  // The previous query made by the settings supplied
  let preQuery = '';

  /* Render the widget */
  ArticleArchiveWidget.prototype.render = (page, overwrite, settings, callbackFunc) => {
    isMoreElements = true;


    // Building the query
    let q = '';
    if (settings.year != null) {
      q += `&year=${settings.year}`;
    }
    if (settings.month != null) {
      q += `&month=${settings.month}`;
    }


    // We got a new query! Set new query and reset more_elements
    if (q !== preQuery) {
      preQuery = q;
      isMoreElements = true;
    }


    let urlParams = '?format=json';
    if (settings.tag) {
      urlParams += `&tags=${settings.tag}`;
      urlParams += `&page=${settings.tagPage}`;
    }
    if (settings.year != null || settings.month != null) {
      urlParams += q;
    }

    if (!settings.tag && !settings.year && !settings.month) {
      // If no filtering, use page supplied
      urlParams += `&page=${page}`;
    }


    // Only call the method if we have more elements
    if (isMoreElements) {
      // The api-call
      makeApiRequest({
        url: `/api/v1/articles/${urlParams}`,
        method: 'GET',
        data: {},
        success(data) {
          // Variables
          let output = '';
          const articles = data.results;
          const maxLength = (settings.archive) ? 10 : 8;
          // Set length of loop to 8 if num articles is more than 8.
          const length = (articles.length > maxLength) ? maxLength : articles.length;

          for (let i = 0; i < length; i += 1) {
            // The markup

            // Because not all images are responsiveimage yet,
            // will be removed later
            if (!articles[i].image) {
              articles[i].image = '';
            }

            output += `
              <div class="row">
                <div class="col-md-12 article${(page === 1 && !overwrite) ? '' : ' article-hidden'}">
                  <div class="row">
                    <div class="col-md-4">
                      <div class="row">
                        <a href="/article/${articles[i].id}/${articles[i].slug}">
                          <img src="${articles[i].image.sm}" width="100%" alt="${articles[i].heading}" />
                        </a>
                      </div>
                    </div>
                    <div class="col-md-8">
                      <div class="pull-right article-detail-meta">
                        <span>${moment(articles[i].published_date).format('DD.MM.YYYY')}</span>
                      </div>
                      <a href="/article/${articles[i].id}/${articles[i].slug}">
                        <h3>${articles[i].heading}</h3>
                      </a>
                      <p>${articles[i].ingress_short}</p>
                      <div class="meta">
                        <div class="row">
                          <div class="col-md-12">
                            <p><strong>Skrevet av: </strong>${articles[i].authors}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>`;
          }


          // Checking to see if we have no more elements
          isMoreElements = data.next != null;


          // Wrapping up the chunk
          output += '</div>';

          // Appending the content.
          // Either appending content or replacing it based on parameters supplied
          if (overwrite) {
            // We are overwriting existing articles
            if ($('.article:visible').length > 0) {
              $('.article:visible').fadeOut(400, () => { // Fade out the visible ones
                if ($('.article:animated').length === 0) { // When all the fading out is done, continue
                  $('#article_archive_container').html(output); // Appending content
                  $('#article_archive_container .article-hidden').fadeIn(400); // Aaaand finally fading in again
                }
              });
            } else {
              $('#article_archive_container').html(output); // Appending content
              $('#article_archive_container .article-hidden').fadeIn(400); // Aaaand finally fading in again
            }
          } else {
            // We are just appending articles
            $('#article_archive_container').append(output);

            // If we are not on the first page, animate them in!
            if (page !== 1) {
              $('#article_archive_container .article-hidden').fadeIn(400);
            }
          }

          // If supplied a callback function, execute it
          if (callbackFunc instanceof Function) {
            callbackFunc();
          }
        },
      });
    } else if (callbackFunc instanceof Function) {
      callbackFunc();
    }
  };
}

export default ArticleArchiveWidget;
