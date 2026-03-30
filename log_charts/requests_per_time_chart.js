/*
  This module implements a chart to display number of requests per time period.
*/

import { addTimeSliderCallBack, getSliderPosition, getRows, getTimeLabels, getTimeUnits } from './controls_handler.js';

let chartId;

export function requestsPerTimeChart(chartIdArg) {
  chartId = chartIdArg;
  addTimeSliderCallBack(renderChart);
  renderChart();
}

function renderChart() {
  const [units, time_column] = getTimeUnits();
  const timeLabels = getTimeLabels();
  const [currentStartIndex, currentEndIndex] = getSliderPosition();

  // Slice the timelabel for the the slider start/end index
  const slicedTimeLabels = timeLabels.slice(currentStartIndex, currentEndIndex + 1);

  // Compute Y values for each timeLabel
  const rowValues = [];
  const rows = getRows();
  const counts = new Map();
  rows.forEach(row => {
    const timeKey = row[time_column]
    counts.set(timeKey, (counts.get(timeKey) || 0) + 1);
  });
  slicedTimeLabels.forEach(timeLabel => {
    rowValues.push(counts.get(timeLabel) || 0);
  });

  // Draw the chart in the chartId HTML element.
  Plotly.react(chartId, [
    {
      x: slicedTimeLabels,
      y: rowValues,
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#14213d', size: 6 },
      line: { shape: 'linear', color: '#fca311', width: 3 },
      hovertemplate: '%{x}<br>Requests: %{y}<extra></extra>',
    },
  ], {
    title: `Requests per ${units}`,
    xaxis: {
      title: units,
      tickangle: -45,
      automargin: true,
    },
    yaxis: {
      title: 'Request Count',
      rangemode: 'tozero',
    },
    margin: { t: 60, r: 24, l: 60, b: 120 },
    paper_bgcolor: '#f2f4f8',
    plot_bgcolor: '#ffffff',
  }, { responsive: true });
}

