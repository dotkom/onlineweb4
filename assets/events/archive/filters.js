import Urls from 'urls';
import $ from 'jquery';

class Filters {
  constructor() {
    this.query = '';
    this.future = true;
    this.myevents = false;
  }

  static showResult(result) {
    $('#events').empty();
    $('#events').append(result);
  }

  static scrollToClosestEvent() {
    const menuOffset = $('nav.subnavbar').position().top + $('nav.subnavbar').outerHeight(true);
    // Scroll to closest event
    const articles = $('#events article');
    const today = new Date();
    articles.each((i, event) => {
      const eventDate = new Date($(event).data('date'));
      if (eventDate < today) {
        // Scroll animation
        $('html, body').animate({ scrollTop: $(event).offset().top - menuOffset }, 250);
        // Break each loop
        return false;
      }
      return true;
    });
  }

  bindEventListeners() {
    // Events
    this.toggleFuture = this.toggleFuture.bind(this);
    this.toggleMyEvents = this.toggleMyEvents.bind(this);
    this.updateQuery = this.updateQuery.bind(this);

    // Elements
    const searchInput = document.getElementById('search');
    const futureCheckbox = document.getElementById('future');
    const myeventsCheckbox = document.getElementById('myevents');

    // Binding event listeners
    searchInput.addEventListener('keyup', this.updateQuery);
    futureCheckbox.addEventListener('click', this.toggleFuture);
    if (myeventsCheckbox !== null) {
      myeventsCheckbox.addEventListener('click', this.toggleMyEvents);
    }
  }

  updateQuery(e) {
    this.query = e.target.value;
    this.search();
  }

  toggleFuture() {
    this.future = !this.future;
    this.search();
  }

  toggleMyEvents() {
    this.myevents = !this.myevents;
    this.search();
  }

  apiUrl() {
    const filters = `?query=${this.query}&future=${this.future}&myevents=${this.myevents}`;
    return Urls.search_events() + filters;
  }

  search() {
    $.get(this.apiUrl(), (result) => {
      Filters.showResult(result);
      if (!this.future) {
        Filters.scrollToClosestEvent();
      }
    });
  }
}

export default Filters;
