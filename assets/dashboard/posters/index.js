import $ from 'jquery';
import assignToJob from './assignToJob';
import './less/posters.less';

$('div.order').each((i, row) => {
  $(row).find('button.assign').click(function assign() {
    assignToJob($(this).val(), row);
  });
});
