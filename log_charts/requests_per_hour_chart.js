import { addTimeSliderCallBack, getSliderState } from './controls_handler.js';

let chartId;

export function requestsPerHourChart(chartIdArg) {
  chartId = chartIdArg;
  addTimeSliderCallBack(renderChart);
  renderChart();
}

function renderChart() {
  const [allLabels, allValues, currentStartIndex, currentEndIndex] = getSliderState();
  const labels = allLabels.slice(currentStartIndex, currentEndIndex + 1);
  const values = allValues.slice(currentStartIndex, currentEndIndex + 1);

  Plotly.react(chartId, [
    {
      x: labels,
      y: values,
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#14213d', size: 6 },
      line: { shape: 'linear', color: '#fca311', width: 3 },
      hovertemplate: '%{x}<br>Requests: %{y}<extra></extra>',
    },
  ], {
    title: 'Requests per Hour',
    xaxis: {
      title: 'Hour',
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

