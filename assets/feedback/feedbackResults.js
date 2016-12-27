import $ from 'jquery';
import { csrfSafeMethod } from 'common/utils/csrf';

// The code was loading twice, this is an ugly fix to prevent that.
let pageInitialized = false;

const initialize = () => {
  // TODO: Avoid semi global variables like these
  let fosChart;
  let mcCharts;

    /* AJAX SETUP FOR CSRF */
  $.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
      }
    },
  });
    /* END AJAX SETUP */

  function printFosChart(data) {
    if (data.length > 0) {
      $('#field-of-study-header').append('<div class="page-header"><h2>Studieretning</h2></div>');

      const box = '<div class="col-md-8"><div id="fos-graph"></div></div>';
      $('#field-of-study-graph').append(box);
      fosChart = $.jqplot('fos-graph', [data],
        {
          grid: {
            drawBorder: false,
            drawGridlines: false,
            background: '#ffffff',
            shadow: false,
          },
          seriesDefaults:
          {
            renderer: $.jqplot.PieRenderer,
            rendererOptions:
            {
              showDataLabels: true,
              dataLabels: 'value',
              sliceMargin: 10,
            },
          },
          legend:
          {
            show: true,
            location: $(window).width() > 991 ? 'e' : 's',
            fontSize: '15pt',
            border: 'none',
          },
        });
    }
  }

  function printRatingCharts(ratings, titles) {
    const ratingCharts = [];

    if (ratings.length > 0) {
      $('#rating-header').append('<div class="page-header"><h2>Vurderinger</h2></div>');
    }

    for (let i = 0; i < titles.length; i += 1) {
      const box = `<div class="col-md-6 rating-chart"><div id="rating-chart-${i}"></div></div>`;
      $('#rating-graphs').append(box);
      const ticks = Array.range(1, ratings[i].length, 1);
      const title = titles[i];

      ratingCharts[i] = $.jqplot(`rating-chart-${i}`, [ratings[i]],
        {
          title,
          seriesDefaults:
          {
            renderer: $.jqplot.BarRenderer,
            pointLabels:
            {
              show: true,
              hideZeros: true,
              formatString: '%d',
            },
          },
          axes:
          {
            xaxis:
            {
              renderer: $.jqplot.CategoryAxisRenderer,
              ticks,
            },
            yaxis:
            {
              tickOptions: { show: false },
            },
          },
          grid:
          {
            gridLineColor: '#FFF',
            drawBorder: false,
          },
        });
    }
  }

  function printMultipleChoiceCharts(data, questions) {
    mcCharts = [];
    if (questions.length > 0) {
      $('#multiple-choice-header').append('<div class="page-header"><h2>Flervalgspørsmål</h2></div>');
    }

    for (let i = 0; i < questions.length; i += 1) {
      const box = `<div class="col-md-6"><div id="mc-chart-${i}"></div></div>`;
      $('#multiple-choice-graphs').append(box);
      const question = questions[i];
      mcCharts[i] = $.jqplot(`mc-chart-${i}`, [data[i]],
        {
          title: question,
          grid: {
            drawBorder: false,
            drawGridlines: false,
            background: '#ffffff',
            shadow: false,
          },
          seriesDefaults:
          {
            renderer: $.jqplot.PieRenderer,
            rendererOptions:
            {
              showDataLabels: true,
              dataLabels: 'value',
              sliceMargin: 10,
            },
          },
          legend:
          {
            show: true,
            location: $(window).width() > 991 ? 'e' : 's',
            fontSize: '15pt',
            border: 'none',
          },
        });
    }
  }

  Array.range = function (a, b, step) {
    let A = [];
    if (typeof a === 'number') {
      A[0] = a;
      step = step || 1;
      while (a + step <= b) {
        A[A.length] = a += step;
      }
    } else {
      let s = 'abcdefghijklmnopqrstuvwxyz';
      if (a === a.toUpperCase()) {
        b = b.toUpperCase();
        s = s.toUpperCase();
      }
      s = s.substring(s.indexOf(a), s.indexOf(b) + 1);
      A = s.split('');
    }
    return A;
  };

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
        const utils = new window.Utils();
        if (res.status === 412) {
          const jsonResponse = JSON.parse(res.responseText);
          utils.setStatusMessage(jsonResponse.message, 'alert-danger');
        } else {
          utils.setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
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

              // change the size of different charts when the screen size changes
      $(window).on('debouncedresize', () => {
        // Checking if window is less than 992px of width.
        // If so, location of text is south (s) of the graph. If not, the location is east (e)
        if ($(window).width() < 992) {
          for (let i = 0; i < mcCharts.length; i += 1) {
            mcCharts[i].replot({
              legend:
              {
                location: 's',
              },
            });
          }

          fosChart.replot({
            legend:
            {
              location: 's',
            },
          });
        } else {
          for (let i = 0; i < mcCharts.length; i += 1) {
            mcCharts[i].replot({
              legend:
              {
                location: 'e',
              },
            });
          }

          fosChart.replot({
            legend:
            {
              location: 'e',
            },
          });
        }

        // Difficult to replot this section. Better solution needed.
        /* for(var i = 0; i < ratingCharts.length; i++)
        {
            ratingCharts[i].replot({ data: options });
            console.log('Fikser graf nummer ' + i);
        }*/
      });


      $('tr').each((i, row) => {
        $(row).find('.icon').click(() => {
          const answerId = $(row).find('td.answer-id').text();
          deleteAnswer(answerId, row);
        });
      });

      // Adds and removes class that controls whitespace between columns on feedback results page.
      $(window).on('debouncedresize', () => {
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

      // Doesnt work properly yet. Will need rework.
      // Should fix height of graph-container if window-width was less than a certain number.
      /* console.log($(window).width());
      if($(window).width() < 992){
          $('#fos-graph').css('height', "500px");
          console.log("small'ne");
          console.log($(window).width());
      }*/

      pageInitialized = true;
    }
  });
};

export default initialize;
