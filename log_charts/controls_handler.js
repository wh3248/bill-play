/*
  This module contains function to handle events from the slider and bucket size controls
  in the HTML file. This also holds the loaded rows from the CSV file and provides information
  and the slider positions and data back to the various charts.
 */

import { loadCsv } from './load_csv.js';

let currentStartIndex = 0;
let currentEndIndex = 0;
let startSlider;
let endSlider;
let startLabel;
let endLabel;
let statusElement;

let csvData = {};
let callBackList = [];

export async function loadControlsHtml(placeHolderId, htmlFile) {
  await fetch(htmlFile)
    .then(r => r.text())
    .then(html => {
      document.getElementById(placeHolderId).innerHTML = html;
    })
}

/*
 * Add a callback function from a chart to call a function in the chart
 * when a slider low or high value changes.
 * Example call to callback:  callBack(True, value) for low value changed with the new value.
 */
export function addTimeSliderCallBack(callBack) {
  if (callBackList.indexOf(callBack) == -1) {
    callBackList.push(callBack);
  }
}

export function getTimeBucket() {
  const timeBucket = document.querySelector('input[name="timeBucket"]:checked').value;
  if (timeBucket == "daily") {
    return ["Day", "day_date", "Daily"];
  } else if (timeBucket == "hourly") {
    return ["Hour", "hour_date", "Hourly"];
  } else {
    return ["Second", "time", "Seconds"];
  }
}
export function getTimeLabels() {
  const timeBucketElement = document.querySelector('input[name="timeBucket"]:checked');
  const timeBucket = timeBucketElement ? timeBucketElement.value : "daily";
  if (!csvData) return [];
  if (timeBucket == "daily") {
    return csvData["dailyLabels"];
  } else {
    return csvData["hourlyLabels"];
  }
}

export function getSliderPosition() {
  return [currentStartIndex, currentEndIndex];
}
/*
 * Get the slider labels, values in start/end index of slider position.
 * Returns:
 *   A list [allLabels, allValues, currentStartIndex, currentEndIndex]
 */
export function getRows() {
  return csvData["rows"];
}

export function timeSliderHandler() {
  loadChartPage()
  .then(chartPage => {
  loadCsv('cleaned_logs.csv')
    .then(data => {
      csvData = data;
      intializeSliderHandler();
      updateSliderLabels();
      chartPage.charts.forEach(element => {
        element.chartFunction(element.chartId);
      });
    })
    .catch(error => {
      console.error(error);
      const status = document.getElementById('status');
      status.textContent = error.message;
      status.classList.add('error');
    });

  })
}

async function loadChartPage() {
  const url = new URL(window.location.href);
  const pageQueryParam = url.searchParams.get("page");
  const pageName = pageQueryParam ? pageQueryParam : "default";
  const chartPagesUrl = "chart_pages.json";
  const response = await fetch(chartPagesUrl);
  if (!response.ok) {
    throw new Error(`Unable to chart definition file ${chartPagesUrl}: ${response.status} ${response.statusText}`);
  }
  const contents = await response.text();
  const chartsJson = JSON.parse(contents);
  const chartPage = chartsJson[pageName];
  let i;
  for (i = 0; i < chartPage.charts.length; i++) {
    let chart = chartPage.charts[i];
    const module = await import(`./${chart.js_file}`);
    const chartFunction = module[chart.js_function];
    chart["chartFunction"] = chartFunction;
    chart["chartId"] = `chart_${i+1}`;
  }
  return chartPage;
}

function intializeSliderHandler() {
  const allLabels = getTimeLabels();
  startSlider = document.getElementById("startSlider");
  endSlider = document.getElementById("endSlider");
  startLabel = document.getElementById("startLabel");
  endLabel = document.getElementById("endLabel");
  statusElement = document.getElementById("status");

  if (!startSlider || !endSlider || !startLabel || !endLabel) {
    throw new Error('Unable to initialize chart controls: one or more element IDs are invalid.');
  }
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
  document.getElementById("dailyTimeBucket").addEventListener('input', () => updateTimeRange(true));
  document.getElementById("hourlyTimeBucket").addEventListener('input', () => updateTimeRange(true));
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
  callBackList.forEach(callBack => {
    callBack();
  });
  const allLabels = getTimeLabels();
  if (statusElement) {
    statusElement.textContent =
      `Displaying ${currentEndIndex - currentStartIndex + 1} hours from ${allLabels[currentStartIndex]} to ${allLabels[currentEndIndex]}.`;
  }
}

function updateSliderLabels() {
  const [units] = getTimeBucket();
  const allLabels = getTimeLabels();
  if (allLabels && allLabels.length > 0 && startLabel && endLabel) {
    startLabel.textContent = allLabels[currentStartIndex] || '—';
    endLabel.textContent = allLabels[currentEndIndex] || '—';
    document.getElementById("startTimeUnits").innerHTML = units;
    document.getElementById("endTimeUnits").innerHTML = units;
  }
}
