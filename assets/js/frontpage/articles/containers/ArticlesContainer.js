import React, { Component } from 'react';
import Articles from '../components/Articles';


const apiArticlesToArticles = (article) => ({
  articleUrl: article.absolute_url,
  ingress: article.ingress_short,
  heading: article.heading,
  image: article.image,
});


class ArticlesContainer extends Component {
  constructor(props) {
    super(props);
    this.API_URL = '/api/v1/articles?format=json';
    this.state = {
      articles: [],
    };
    this.fetchArticles();
  }

  fetchArticles() {
    const apiUrl = this.API_URL;
    fetch(apiUrl, { credentials: 'same-origin' })
    .then(response => response.json())
    .then((json) => {
      this.setState({
        articles: json.results.map(apiArticlesToArticles),
      });
    });
  }

  mainArticles() {
    return this.state.articles.slice(0, 2);
  }

  smallArticles() {
    return this.state.articles.slice(2, 8);
  }

  render() {
    return (
      <Articles
        mainArticles={this.mainArticles()} smallArticles={this.smallArticles()}
      />
    );
  }
}

export default ArticlesContainer;
