
//The code was loading twice, this is an ugly fix to prevent that.
var pageInitialized = false;

$(function() {
    /* AJAX SETUP FOR CSRF */
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    /* END AJAX SETUP */

    function printFosChart(data)
    {
        if(data.length > 0)
        {
            $('#field-of-study-header').append('<div class="page-header"><h2>Studieretning</h2></div>');

            box = '<div class="col-md-8"><div id="fos-graph"></div></div>'
            $('#field-of-study-graph').append(box);
            fosChart = jQuery.jqplot ('fos-graph', [data], 
            {
                grid: {
                    drawBorder: false, 
                    drawGridlines: false,
                    background: '#ffffff',
                    shadow:false
                },
                seriesDefaults: 
                {
                    renderer: jQuery.jqplot.PieRenderer, 
                    rendererOptions: 
                    {
                        showDataLabels: true,
                        dataLabels: 'value',
                        sliceMargin: 10
                    }
                }, 
                legend: 
                { 
                    show:true, 
                    location: $(window).width() > 991 ? 'e' : 's',
                    fontSize: '15pt',
                    border: 'none'
                }
            });
        }
    }

    function printRatingCharts(ratings, titles) 
    {
        ratingCharts = new Array();

        if(ratings.length > 0){
            $('#rating-header').append('<div class="page-header"><h2>Vurderinger</h2></div>');
        }

        for(var i = 0; i < titles.length; i++)
        {   
            box = '<div class="col-md-6 rating-chart"><div id="rating-chart-' + i + '"></div></div>'
            $('#rating-graphs').append(box);
            ticks = Array.range(1, ratings[i].length, 1);
            title = titles[i];

            ratingCharts[i] = $.jqplot('rating-chart-' + i, [ratings[i]], 
            {
                title: title,
                seriesDefaults:
                {
                    renderer:$.jqplot.BarRenderer,
                    pointLabels: 
                    {
                        show: true, 
                        hideZeros: true,
                        formatString: '%d',
                    }
                },
                axes: 
                {
                    xaxis: 
                    {
                        renderer: $.jqplot.CategoryAxisRenderer,
                        ticks: ticks,
                    },
                    yaxis:
                    {
                        tickOptions: { show: false}
                    },
                },
                grid: 
                { 
                    gridLineColor: '#FFF',
                    drawBorder: false,    
                }
            });
        }
    }

    function printMultipleChoiceCharts(data, questions)
    {
        mcCharts = new Array();
        if(questions.length > 0){
            $('#multiple-choice-header').append('<div class="page-header"><h2>Flervalgspørsmål</h2></div>');
        }

        for(i = 0; i < questions.length; i++)
        {   
            box = '<div class="col-md-6"><div id="mc-chart-' + i + '"></div></div>'
            $('#multiple-choice-graphs').append(box);
            question = questions[i];
            mcCharts[i] = $.jqplot('mc-chart-' + i, [data[i]], 
            {
                title: question,
                grid: {
                    drawBorder: false, 
                    drawGridlines: false,
                    background: '#ffffff',
                    shadow:false
                },
                seriesDefaults: 
                {
                    renderer: jQuery.jqplot.PieRenderer, 
                    rendererOptions: 
                    {
                        showDataLabels: true,
                        dataLabels: 'value',
                        sliceMargin: 10
                    }
                }, 
                legend: 
                { 
                    show:true, 
                    location: $(window).width() > 991 ? 'e' : 's',
                    fontSize: '15pt',
                    border: 'none'
                }
            });
        }
    }

    Array.range= function(a, b, step){
        var A= [];
        if(typeof a== 'number'){
            A[0]= a;
            step= step || 1;
            while(a+step<= b){
                A[A.length]= a+= step;
            }
        }
        else{
            var s= 'abcdefghijklmnopqrstuvwxyz';
            if(a=== a.toUpperCase()){
                b=b.toUpperCase();
                s= s.toUpperCase();
            }
            s= s.substring(s.indexOf(a), s.indexOf(b)+ 1);
            A= s.split('');        
        }
        return A;
    }

    function deleteAnswer(answer, row)
    {
        $.ajax({
            method: 'POST',
            url: '/feedback/deleteanswer/',
            data: {'answer_id':answerId, },
            success: function() {
                // TODO Make animation
                $(row).hide();
            },
            error: function(res) {
                var utils = new Utils();
                if (res['status'] === 412) {
                    res = JSON.parse(res['responseText']);
                    utils.setStatusMessage(res['message'], 'alert-danger');
                }
                else {
                    utils.setStatusMessage('En uventet feil ble oppdaget. Kontakt dotkom@online.ntnu.no for assistanse.', 'alert-danger');
                }
            },
            crossDomain: false
        });
    }

    $(document).ready(function()
    {
        if(!pageInitialized)
        {

            $.get("chartdata/", function(data)
            {
                printFosChart(data.replies.fos);
                printRatingCharts(data.replies.ratings, data.replies.titles);
                printMultipleChoiceCharts(data.replies.mc_answers, data.replies.mc_questions);
            });

              // change the size of different charts when the screen size changes
             $(window).on("debouncedresize", function(e)
             {
                // Checking if window is less than 992px of width. If so, location of text is south (s) of the graph. If not, the location is east (e)
                if($(window).width() < 992){
                    for(i = 0; i < mcCharts.length; i++){
                        mcCharts[i].replot({
                            legend: 
                            { 
                                location: 's',
                            }
                        });
                    }

                    fosChart.replot({
                        legend: 
                        { 
                            location: 's',
                        }
                    });
                }
                else{
                    for(i = 0; i < mcCharts.length; i++){
                        mcCharts[i].replot({
                            legend: 
                            { 
                                location: 'e',
                            }
                        });
                    }

                    fosChart.replot({
                        legend: 
                        { 
                            location: 'e',
                        }
                    });
                }

                // Difficult to replot this section. Better solution needed.
               /* for(var i = 0; i < ratingCharts.length; i++)
                {
                    ratingCharts[i].replot({ data: options });
                    console.log('Fikser graf nummer ' + i);
                }*/
             });


            $('tr').each(function(i, row)
            {
                $(row).find('.icon').click(function()
                {
                    answerId = $(row).find('td.answer-id').text();
                    deleteAnswer(answerId, row);
                });
            });

            // Adds and removes class that controls whitespace between columns on feedback results page.
            $(window).on("debouncedresize", function(e)
            {
               if($(window).width() < 992){
                    $('div.specifier').removeClass('whitespaceFix');
               }

               if($(window).width() > 991){
                    $('div.specifier').addClass('whitespaceFix');
               }
            });

            // if width of screen is less than 992px, remove class whitespaceFix, which sets every even column to float: right
            if($(window).width() < 992){
                $('div.specifier').removeClass('whitespaceFix');
            }

            // Doesnt work properly yet. Will need rework. Should fix height of graph-container if window-width was less than a certain number.
           /* console.log($(window).width());
            if($(window).width() < 992){
                $('#fos-graph').css('height', "500px");
                console.log("small'ne");
                console.log($(window).width());
            }*/

            pageInitialized = true;
        }
    });
});


