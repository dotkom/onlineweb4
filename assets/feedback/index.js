import AnswerRating from './answerRating';
import FeedBackResults from './feedbackResults';


// Check if bar rating should be initialized
const ratingWrapper = document.querySelector('.rating-wrapper');
if (ratingWrapper !== null) {
  AnswerRating();
}

// Check if feed back results charts should be initialized
const feedBackResultsElement = document.getElementById('feedback-results');
if (feedBackResultsElement !== null) {
  FeedBackResults();
}
