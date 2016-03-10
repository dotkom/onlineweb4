
var inventoryGraphs = function(){
    var jsonData

    function drawChart() {

        console.log(jsonData)

        var data = new google.visualization.DataTable();

        data.addColumn('string', "Vare")
        data.addColumn('number', "Antall")

        for (var key in jsonData) {
          if (jsonData.hasOwnProperty(key)) {
            data.addRow([key, jsonData[key]])
          }
        }

      var view = new google.visualization.DataView(data);

      var options = {
        title: "Varesalg",
        height: 500,
        bar: {groupWidth: "95%"},
        legend: { position: "none" },
      };
      var chart = new google.visualization.ColumnChart(document.getElementById("columnchart_values"));
      chart.draw(view, options);
    }

    $.getJSON( "orders/", function( data ) {
        jsonData = data
        google.charts.load("current", {packages:['corechart']});
        google.charts.setOnLoadCallback(drawChart);
    });
}

inventoryGraphs()


