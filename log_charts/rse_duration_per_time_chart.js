/*
  This module implements a chart to display number of duration per time period.
*/

import { addTimeSliderCallBack, getSliderPosition, getRows, getTimeLabels, getTimeUnits, isTestingUser } from './controls_handler.js';

let chartId;

export function durationPerTimeChart(chartIdArg) {
  chartId = chartIdArg;
  addTimeSliderCallBack(renderChart);
  renderChart();
}

function renderChart() {
  const [units, bucket] = getTimeUnits();
  const timeLabels = getTimeLabels();
  const [currentStartIndex, currentEndIndex] = getSliderPosition();

  // Slice the timelabel for the the slider start/end index
  const slicedTimeLabels = timeLabels.slice(currentStartIndex, currentEndIndex + 1);

  // Get max duration per time bucket into a map
  const allValuesMaxDurationMap = new Map();
  const rseValuesMaxDurationMap = new Map();
  const allValues = [];
  const rseValues = [];
  const rows = getRows();
  rows.forEach(row => {
    const timeKey = row[bucket];
    const duration = parseFloat(row["duration"]);
    let maxValue = allValuesMaxDurationMap.get(timeKey) || 0.0;
    maxValue = Math.max(maxValue, duration);
    allValuesMaxDurationMap.set(timeKey, maxValue);
    if (isTestingUser(row)) {
      rseValuesMaxDurationMap.set(timeKey, maxValue);
    }
  });

  // Compute Y values for each timeLabel
  slicedTimeLabels.forEach(timeLabel => {
    allValues.push(allValuesMaxDurationMap.get(timeLabel) || 0);
    rseValues.push(rseValuesMaxDurationMap.get(timeLabel) || 0);
  });

  // Draw the chart in the chartId HTML element.
  Plotly.react(chartId, [
    {
      x: slicedTimeLabels,
      y: allValues,
      name: 'All users',
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#fca311', size: 6 },
      line: { shape: 'linear', color: '#fca311', width: 3 },
      hovertemplate: '%{x}<br>Requests: %{y}<extra></extra>',
    },
    {
      x: slicedTimeLabels,
      y: rseValues,
      name: 'Team testing requests',
      type: 'scatter',
      mode: 'lines+markers',
      marker: { symbol: 'x', color: '#2f4b7c', size: 8 },
      line: { shape: 'linear', color: '#2f4b7c', width: 3, dash: 'dash' },
      hovertemplate: '%{x}<br>Testing requests: %{y}<extra></extra>',
    },
  ], {
    title: `Longest Query per ${units} with Team Testing Requests`,
    xaxis: {
      title: units,
      tickangle: -45,
      automargin: true,
    },
    yaxis: {
      title: `Max Duration(s) for ${units}`,
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

