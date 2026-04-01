/*
  This module implements a chart to display number of requests per time period.
*/

import { addTimeSliderCallBack, getSliderPosition, getRowsInDateRange, getTimeLabels, getTimeUnits, isTestingUser} from './controls_handler.js';

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
  const rows = getRowsInDateRange();
  rows.forEach(row => {
    const timeKey = row[time_column]
    const user_id = row["user_id"];
    allCountsMap.set(timeKey, (allCountsMap.get(timeKey) || 0) + 1);
    if (isTestingUser(row)) {
      rseCountsMap.set(timeKey, (rseCountsMap.get(timeKey) || 0) + 1);
    }
  });

  // Compute Y values for each timeLabel
  slicedTimeLabels.forEach(timeLabel => {
    allCountValues.push(allCountsMap.get(timeLabel) || 0);
    rseCountValues.push(rseCountsMap.get(timeLabel) || 0);
  });

  // Draw the chart in the chartId HTML element.
  Plotly.react(chartId, [
    {
      x: slicedTimeLabels,
      y: allCountValues,
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#fca311', size: 6 },
      line: { shape: 'linear', color: '#fca311', width: 3 },
      hovertemplate: '%{x}<br>Requests: %{y}<extra></extra>',
    },
  ], {
    title: `# Requests per ${units}`,
    xaxis: {
      title: units,
      tickangle: -45,
      automargin: true,
      type: 'date',
      tickformat: units === 'Day' ? '%Y-%m-%d' : undefined,
    },
    yaxis: {
      title: `# Request per ${units}`,
      rangemode: 'tozero',
    },
    margin: { t: 35, r: 24, l: 60, b: 5 },
    paper_bgcolor: '#f2f4f8',
    plot_bgcolor: '#ffffff',
  }, { responsive: true });
}

