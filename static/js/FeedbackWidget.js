function createFoschart(chartdata) {

    var width = 700,
        height = 400,
        chartWidth = 400,
        chartHeight = 400,
        radius = Math.min(chartWidth, chartHeight) / 2;

    var color = d3.scale.category10();

    fosdata = chartdata
   
    var color_hash = { 0 :  ['Bachelor i Informatikk (BIT)', "cyan"],
                       1 :  ['Intelligente Systemer (IRS)', "pink"],
                       2 :  ['Software (SW)', "yellow"],
                       3 :  ['Informasjonsforvaltning (DIF)', "green"],
                       4 :  ['Komplekse Datasystemer (KDS)', "gray"],
                       5 :  ['Spillteknologi (SPT)', "purple"]
    }


    arc = d3.svg.arc()
        .outerRadius(radius - 10)
        .innerRadius(0);

    var pie = d3.layout.pie()
        .sort(null)
        .value(function(d) { return d.value; });

    var svg = d3.select("#foschart")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("transform", "translate(" + chartWidth / 2 + "," + chartHeight / 2 + ")");

    var legend = svg.selectAll(".legend")
        .data(fosdata)
      .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) { return "translate(0," + ((i * 20) - 100) + ")"; });

    legend.append("rect")
        .attr("x", chartWidth + 55)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", function(d) { return color_hash[fosdata.indexOf(d)][1]; })

    legend.append("text")
        .attr("x", chartWidth + 50)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) { return color_hash[fosdata.indexOf(d)][0]; });


    var g = svg.selectAll(".arc")
        .data(pie(fosdata))
      .enter().append("g")
        .attr("class", "arc");

    g.append("path")
        .attr("d", arc)
        .data(fosdata)
        .attr("fill", function(d) { 
            var color = color_hash[fosdata.indexOf(d)][1];
            return color;})

}

function createRatingCharts(chartdata) {
    for (var index = 0; index < chartdata.length; index++) {
        var margin = {top: 20, right: 20, bottom: 30, left: 40},
                            width = 570- margin.left - margin.right,
            height = 350 - margin.top - margin.bottom;
        
        var x = d3.scale.ordinal()
            .rangeRoundBands([0, width], .1);

        var y = d3.scale.linear()
            .rangeRound([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left")
            .tickFormat(d3.format("0"));

        var svg = d3.select("#ratingcharts").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        x.domain(chartdata[index].map(function(d, i) { return i + 1; }));
        y.domain([0, d3.max(chartdata[index], function(d, i) { return chartdata[index][i]; })]);

        var color = ["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]; 
 
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);
          

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
          .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("stemmer");

        svg.selectAll(".bar")
            .data(chartdata[index])
          .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function(d, i) { return i * 83 + 26; })
            .attr("width", 40)
            .attr("y", function(d) { return y(d); })
            .attr("height", function(d, i) { return height - y(chartdata[index][i]); })
            .style("fill", function(d, i) { return color[i]; });

    }
}
