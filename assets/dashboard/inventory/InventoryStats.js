import $ from 'jquery';
import google from 'google';

const inventoryGraphs = () => {
  let jsonData = {};

  function drawChart() {
    const data = new google.visualization.DataTable();

    data.addColumn('string', 'Vare');
    data.addColumn('number', 'Antall');

    Object.keys(jsonData).forEach((key) => {
      data.addRow([key, jsonData[key]]);
    });

    const view = new google.visualization.DataView(data);

    const options = {
      title: 'Varesalg',
      height: 500,
      bar: { groupWidth: '95%' },
      legend: { position: 'none' },
    };
    const chart = new google.visualization.ColumnChart(document.getElementById('columnchart_values'));
    chart.draw(view, options);
  }

  $.getJSON('orders/', (data) => {
    jsonData = data;
    google.charts.load('current', { packages: ['corechart'] });
    google.charts.setOnLoadCallback(drawChart);
  });
};


export default {
  init: inventoryGraphs,
};
