function printPieChart(data)
{
    var plot1 = jQuery.jqplot ('fieldOfStudyChart', [data], 
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
