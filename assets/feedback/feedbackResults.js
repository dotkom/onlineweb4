// import $ from 'jquery';
import * as echarts from 'echarts';
import { ajaxEnableCSRF, debouncedResize, setStatusMessage } from 'common/utils/';

// The code was loading twice, this is an ugly fix to prevent that.
let pageInitialized = false;

const initialize = () => {
  ajaxEnableCSRF($);

  function printFosChart(data) {
    if (data.length > 0) {
      $('#field-of-study-header').append('<div class="page-header"><h2>Studieretning</h2></div>');

      const box = '<div class="col-md-8"><div id="fos-graph" style="width: 100%; height: 400px;"></div></div>';
      $('#field-of-study-graph').append(box);

      var myChart = echarts.init(document.getElementById('fos-graph'));
      const chartData = data.map((d) => {
        return {
          "value": d[1],
          "name": d[0]
        }
      });

      var option = {
        "title": {
          "text": 'Studieretning'
        },
        "series": [
          {
            "type": 'pie',
            "data": chartData
          }
        ]
      };

      myChart.setOption(option);
    }
  }

  function printRatingCharts(ratings, titles) {
    if (ratings.length > 0) {
      $('#rating-header').append('<div class="page-header"><h2>Vurderinger</h2></div>');
    }

    for (let i = 0; i < titles.length; i += 1) {
      const box = `<div class="col-md-6 rating-chart"><div id="rating-chart-${i}" style="width: 100%; height: 400px;"></div></div>`;
      $('#rating-graphs').append(box);
      const ticks = ratings[i].map((_, index) => index + 1);
      const title = titles[i];

      var myChart = echarts.init(document.getElementById(`rating-chart-${i}`));

      const option = {
        "title": {
          "text": title
        },
        "xAxis": {
          "data": ticks,
        },
        "yAxis": {},
        "series": [
          {
            "type": "bar",
            "data": ratings[i]
          }
        ]
      };

      myChart.setOption(option);
      window.addEventListener('resize', function () {
        myChart.resize();
      });
    }
  }

  function printMultipleChoiceCharts(data, questions) {
    if (questions.length > 0) {
      $('#multiple-choice-header').append('<div class="page-header"><h2>Flervalgspørsmål</h2></div>');
    }

    for (let i = 0; i < questions.length; i += 1) {
      const box = `<div class="col-md-6"><div id="mc-chart-${i}" style="width: 100%; height: 400px;"></div></div>`;
      $('#multiple-choice-graphs').append(box);
      const question = questions[i];
      var myChart = echarts.init(document.getElementById(`mc-chart-${i}`));

      const chartData = data[i].map((d) => {
        return {
          "value": d[1],
          "name": d[0]
        }
      });

      const option = {
        "title": {
          "text": question
        },
        "series": [
          {
            "type": 'pie',
            "data": chartData
          }
        ]
      };

      myChart.setOption(option);
      window.addEventListener('resize', function () {
        myChart.resize();
      });
    }
  }

  function deleteAnswer(answerId, row) {
    $.ajax({
      method: 'POST',
      url: '/feedback/deleteanswer/',
      data: { answer_id: answerId },
      success() {
        // TODO Make animation
        $(row).hide();
      },
      error(res) {
        if (res.status === 412) {
          const jsonResponse = JSON.parse(res.responseText);
          setStatusMessage(jsonResponse.message, 'alert-danger');
        } else {
          setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
        }
      },
      crossDomain: false,
    });
  }

  $(document).ready(() => {
    if (!pageInitialized) {
      $.get('chartdata/', (data) => {
        printFosChart(data.replies.fos);
        printRatingCharts(data.replies.ratings, data.replies.titles);
        printMultipleChoiceCharts(data.replies.mc_answers, data.replies.mc_questions);
      });

      $('tr').each((i, row) => {
        $(row).find('.icon').click(() => {
          const answerId = $(row).find('td.answer-id').text();
          deleteAnswer(answerId, row);
        });
      });

      // Adds and removes class that controls whitespace between columns on feedback results page.
      debouncedResize(() => {
        if ($(window).width() < 992) {
          $('div.specifier').removeClass('whitespaceFix');
        }

        if ($(window).width() > 991) {
          $('div.specifier').addClass('whitespaceFix');
        }
      });

      // if width of screen is less than 992px, remove class whitespaceFix,
      // which sets every even column to float: right
      if ($(window).width() < 992) {
        $('div.specifier').removeClass('whitespaceFix');
      }

      pageInitialized = true;
    }
  });
};

export default initialize;
