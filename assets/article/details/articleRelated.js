import $ from 'jquery';

const addRelatedArticles = (data) => {
  let output = '';
  const articles = data.results;
  // Set length of loop to 6 if num articles is more than 6.
  const len = (articles.length > 6) ? 6 : articles.length;

  for (let i = 0; i < len; i += 1) {
    output += `
      <div class="row-fluid">
        <div class="span12">
          <a href="/article/${articles[i].id}">
            <img src="${articles[i].image.thumb}" alt="${articles[i].heading}">
          </a>
          <br />
          <h4>${articles[i].heading}</h4>
        </div>
      </div>`;
  }

  $('#article-detaill-latest').html(output);
};

export default () => {
  $.ajax({
    url: '/api/v1/articles/?format=json&featured=False',
    method: 'GET',
    data: {},
    addRelatedArticles,
  });
};
