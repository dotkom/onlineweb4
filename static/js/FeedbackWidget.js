function createchart(chartdata) {

    var width = 300,
        height = 300,
        radius = 100

    var color = d3.scale.category20c();

    var data = chartdata

    var vis = d3.select("body")
        .append("svg:svg")
        .data([data])
            .attr("width", width)
            .attr("height", height)
        .append("svg:g")
            .attr("transform", "translate(" + radius + "," + radius + ")")
    
    var arc = d3.svg.arc()
        .outerRadius(radius);

    var pie = d3.layout.pie()
        .value(function(d) { return d.value; });

    var arcs = vis.selectAll("g.slice")
        .data(pie)
        .enter()
            .append("svg:g")
                .attr("class", "slice");
        arcs.append("svg:path")
                .attr("fill", function(d, i) { return color(i); })
                .attr("d", arc);

        arcs.append("svg:text")
                .attr("transform", function(d) {
                    d.innerRadius = 0;
                    d.outerRadius = radius;
                    return "translate(" + arc.centroid(d) + ")";
                })
                .attr("text-anchor", "middle")
                .text(function(d, i) { return data[i].label; });
}
