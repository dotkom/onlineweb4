import FeedBackResults from './feedbackResults';
import './less/feedback.less';


// Check if feed back results charts should be initialized
const feedBackResultsElement = document.getElementById('feedback-results');
if (feedBackResultsElement !== null) {
  FeedBackResults();
}
