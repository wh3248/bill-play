/*
  This module implements a chart to display number of requests per time period.
*/

import { addTimeSliderCallBack, getSliderPosition, getRows, getTimeLabels, getTimeUnits, isTestingUser } from './controls_handler.js';

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

  // Get counts for each time bucket into a map
  const allCountsMap = new Map();
  const rseCountsMap = new Map();
  const allCountValues = [];
  const rseCountValues = [];
  const rows = getRows();
  rows.forEach(row => {
    const timeKey = row[time_column]
    allCountsMap.set(timeKey, (allCountsMap.get(timeKey) || 0) + 1);
    if (isTestingUser(row)) {
      rseCountsMap.set(timeKey, (rseCountsMap.get(timeKey) || 0) + 1);
    }
  });

  // Compute Y vaues for each timeLabel
  slicedTimeLabels.forEach(timeLabel => {
    allCountValues.push(allCountsMap.get(timeLabel) || 0);
    rseCountValues.push(rseCountsMap.get(timeLabel) || 0);
  });

  // Draw the chart in the chartId HTML element.
  Plotly.react(chartId, [
    {
      x: slicedTimeLabels,
      y: allCountValues,
      name: 'All requests',
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#fca311', size: 6 },
      line: { shape: 'linear', color: '#fca311', width: 3 },
      hovertemplate: '%{x}<br>Requests: %{y}<extra></extra>',
    },
    {
      x: slicedTimeLabels,
      y: rseCountValues,
      name: 'Team testing requests',
      type: 'scatter',
      mode: 'lines+markers',
      marker: { symbol: 'x', color: '#2f4b7c', size: 8 },
      line: { shape: 'linear', color: '#2f4b7c', width: 3, dash: 'dash' },
      hovertemplate: '%{x}<br>Testing requests: %{y}<extra></extra>',
    },
  ], {
    title: `Requests Rate per ${units} with Team Testing Requests`,
    xaxis: {
      title: units,
      tickangle: -45,
      automargin: true,
    },
    yaxis: {
      title: `# Request per ${units}`,
      rangemode: 'tozero',
    },
    legend: {
      orientation: 'h',
      x: 0,
      y: .96,
      xanchor: 'left',
      yanchor: 'bottom',
      bgcolor: 'rgba(255,255,255,0.8)',
      bordercolor: '#ccc',
      borderwidth: 1,
    },
    margin: { t: 50, r: 24, l: 60, b: 5 },
    paper_bgcolor: '#f2f4f8',
    plot_bgcolor: '#ffffff',
  }, { responsive: true });
}

