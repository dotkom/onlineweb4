function createchart(chartdata) {

    var width = 500,
        height = 500,
        radius = Math.min(width, height) / 2;

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
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var legend = d3.select("#foschartlegend").append("svg")
        .attr("class", "legend")
        .attr("width", radius * 2)
        .attr("height", radius * 2)
      .selectAll("g")
        .data(fosdata)
      .enter().append("g")
        .attr("transform", function(d, i) { return "translate(0," + ((i * 20) + 100) + ")"; });

    legend.append("rect")
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", function(d) { return color_hash[fosdata.indexOf(d)][1]; })

    legend.append("text")
        .attr("x", 24)
        .attr("y", 9)
        .attr("dy", ".35em")
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
