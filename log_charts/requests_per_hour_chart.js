let allLabels = [];
let allValues = [];
let currentStartIndex = 0;
let currentEndIndex = 0;
let chartId;
let statusId;
let startSlider;
let endSlider;
let startLabel;
let endLabel;

export function formatHourLabel(date) {
  return date.toISOString().slice(0, 13).replace('T', ' ') + ':00';
}

function parseCsvTime(value) {
  if (!value) {
    return null;
  }
  const normalized = value.trim().replace(/\s+/g, ' ');
  const parsed = new Date(normalized);
  return isNaN(parsed) ? null : parsed;
}

export function createHourlyBuckets(rows) {
  const counts = new Map();
  let minDate = null;
  let maxDate = null;

  rows.forEach(row => {
    const timeValue = row.time || row['time'];
    const date = parseCsvTime(timeValue);
    if (!date) {
      return;
    }

    date.setMinutes(0, 0, 0);
    const hourKey = formatHourLabel(date);
    counts.set(hourKey, (counts.get(hourKey) || 0) + 1);

    if (!minDate || date < minDate) minDate = new Date(date);
    if (!maxDate || date > maxDate) maxDate = new Date(date);
  });

  if (!minDate || !maxDate) {
    return { labels: [], values: [] };
  }

  const labels = [];
  const values = [];
  const cursor = new Date(minDate);

  while (cursor <= maxDate) {
    const label = formatHourLabel(cursor);
    labels.push(label);
    values.push(counts.get(label) || 0);
    cursor.setHours(cursor.getHours() + 1);
  }

  return { labels, values };
}

function updateSliderLabels() {
  startLabel.textContent = allLabels[currentStartIndex] || '—';
  endLabel.textContent = allLabels[currentEndIndex] || '—';
}

function renderChart() {
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

function updateTimeRange(isStartChanged) {
  const newStart = parseInt(startSlider.value, 10);
  const newEnd = parseInt(endSlider.value, 10);

  if (newStart > newEnd) {
    if (isStartChanged) {
      endSlider.value = newStart;
      currentStartIndex = newStart;
      currentEndIndex = newStart;
    } else {
      startSlider.value = newEnd;
      currentStartIndex = newEnd;
      currentEndIndex = newEnd;
    }
  } else {
    currentStartIndex = newStart;
    currentEndIndex = newEnd;
  }

  updateSliderLabels();
  renderChart();
  document.getElementById(statusId).textContent =
    `Displaying ${currentEndIndex - currentStartIndex + 1} hours from ${allLabels[currentStartIndex]} to ${allLabels[currentEndIndex]}.`;
}

export function requestsPerHourChart(ids, labels, values, rowCount) {
  chartId = ids.chartId;
  statusId = ids.statusId;
  startSlider = document.getElementById(ids.startSliderId);
  endSlider = document.getElementById(ids.endSliderId);
  startLabel = document.getElementById(ids.startLabelId);
  endLabel = document.getElementById(ids.endLabelId);

  if (!startSlider || !endSlider || !startLabel || !endLabel || !document.getElementById(chartId)) {
    throw new Error('Unable to initialize chart controls: one or more element IDs are invalid.');
  }

  allLabels = labels;
  allValues = values;
  currentStartIndex = 0;
  currentEndIndex = allLabels.length - 1;

  startSlider.min = 0;
  startSlider.max = allLabels.length - 1;
  endSlider.min = 0;
  endSlider.max = allLabels.length - 1;
  startSlider.value = currentStartIndex;
  endSlider.value = currentEndIndex;

  startSlider.addEventListener('input', () => updateTimeRange(true));
  endSlider.addEventListener('input', () => updateTimeRange(false));

  updateSliderLabels();
  renderChart();
  document.getElementById(statusId).textContent =
    `Loaded ${rowCount} rows and bucketed into ${allLabels.length} hourly intervals.`;
}
