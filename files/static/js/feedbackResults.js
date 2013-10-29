function printPieChart(var data)
{
    alert("derp");
    var plot1 = jQuery.jqplot ('field-of-study-chart', [data], 
    { 
        seriesDefaults: 
        {
            renderer: jQuery.jqplot.PieRenderer, 
            rendererOptions: 
            {
                showDataLabels: true
            }
        }, 
        legend: { show:true, location: 'e' }
    });
}

