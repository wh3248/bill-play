/*
  This module implements a chart to display number of duration per time period.
*/

import { addTimeSliderCallBack, getSliderPosition, getRows, getTimeLabels, getTimeBucket } from './controls_handler.js';

let chartId;

export function durationPerTimeChart(chartIdArg) {
  chartId = chartIdArg;
  addTimeSliderCallBack(renderChart);
  renderChart();
}

function renderChart() {
  const [units, bucket] = getTimeBucket();
  const timeLabels = getTimeLabels();
  const [currentStartIndex, currentEndIndex] = getSliderPosition();

  // Slice the timelabel for the the slider start/end index
  const slicedTimeLabels = timeLabels.slice(currentStartIndex, currentEndIndex + 1);

  // Compute Y values for each timeLabel
  const rowValues = [];
  const rows = getRows();
  const max_duration = new Map();
  rows.forEach(row => {
    const timeKey = row[bucket];
    const duration = parseFloat(row["duration"])
    let maxValue = max_duration.get(timeKey) || 0.0;
    maxValue = Math.max(maxValue, duration);
    max_duration.set(timeKey, maxValue);
  });
  slicedTimeLabels.forEach(timeLabel => {
    rowValues.push(max_duration.get(timeLabel) || 0);
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
    title: `Duration per ${units}`,
    xaxis: {
      title: units,
      tickangle: -45,
      automargin: true,
    },
    yaxis: {
      title: `Max Duration(s) for ${units}`,
      rangemode: 'tozero',
    },
    margin: { t: 60, r: 24, l: 60, b: 120 },
    paper_bgcolor: '#f2f4f8',
    plot_bgcolor: '#ffffff',
  }, { responsive: true });
}

