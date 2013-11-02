function printPieChart(data)
{
    var plot1 = jQuery.jqplot ('field-of-study-chart', [data], 
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
            location: 'e',
            fontSize: '15pt',
            border: 'none'
        }
    });
}

function printRatingCharts(data, titles)
{
    for(var i = 0; i < data.length; i++)
    {            
        ticks = Array.range(1, data[i].length, 1);
        $.jqplot('rating-chart-' + (i + 1), [data[i]], 
        {
            title: titles[i],
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
