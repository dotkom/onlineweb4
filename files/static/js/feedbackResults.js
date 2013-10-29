function printPieChart(data)
{
    var plot1 = jQuery.jqplot ('field-of-study-chart', [data], 
    { 
        seriesDefaults: 
        {
            renderer: jQuery.jqplot.PieRenderer, 
            rendererOptions: 
            {
                showDataLabels: true,
                dataLabels: 'value',
                sliceMargin: 4
            }
        }, 
        legend: { show:true, location: 'e' }
    });
}

