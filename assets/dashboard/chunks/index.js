import showdown from 'showdown';
import $ from 'jquery';

let sourceText = '';
let previousSourceText;

function run() {
  previousSourceText = sourceText;
  sourceText = document.getElementById('id_content').value;
  if (previousSourceText === sourceText) {
    return;
  }
  const target = document.getElementById('chunk-content');
  const converter = new showdown.Converter();
  const output = converter.makeHtml(sourceText);
  target.innerHTML = output;
}
// Run once initially to render it first time.
run();
// Render for changes to the data
$('#id_content').on('change keyup', run);
