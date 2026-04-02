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

/**
 * Initialize controls by loading chart page config and CSV data.
 * This sets up sliders, labels, and invokes initial chart rendering.
 */
export function initializeControlsHandler() {
  loadChartDefinitions()
    .then(selectedPage => {
      const chartPage = selectedPage.chartPage;
      const definedPages = selectedPage.definedPages;
      const definitionId = selectedPage.id;
      loadCsv(chartPage.log_file)
        .then(data => {
          csvData = data;
          initializeHeading(definitionId, chartPage, definedPages);
          initializeTimeBucketOption();
          intializeSliders();
          updateSliderLabels();
          updateTimeRange();
          generateCharts(chartPage);
        })
        .catch(error => {
          const status = document.getElementById('status');
          status.textContent = error.message;
          status.classList.add('error');
        });
    })
    .catch(error => {
      const status = document.getElementById('status');
      status.textContent = error.message;
      status.classList.add('error');
    })
}


/**
 * Generate all the charts defined in the chartPage load by the page load.
 * @param {object} chartPage - The object contains the chartId and chartFunctions.
 */
async function generateCharts(chartPage) {
  // make the chart body tags visible/invisible depending on # charts on page
  // also assign the chartId tag to the charts depending on how many charts on page.
  const chartBodyTags = ["body-4-charts", "body-3-charts", "body-2-charts", "body-1-chart"];
  let i;
  chartBodyTags.forEach(tag => {
    const element = document.getElementById(tag);
    if (element) {
      if ((tag == "body-4-charts") && (chartPage.charts.length == 4)) {
        // make the div to display 4 charts visible
        element.style.display = "block";
        for (i = 0; i < chartPage.charts.length; i++) {
          const chart = chartPage.charts[i];
          chart["chartId"] = `chart_${i + 1}`;
        }
      } else if ((tag == "body-3-charts") && (chartPage.charts.length == 3)) {
        // make the div to display 3 charts visible
        element.style.display = "block";
        for (i = 0; i < chartPage.charts.length; i++) {
          const chart = chartPage.charts[i];
          chart["chartId"] = `chart_3_${i + 1}`;
        }
      } else if ((tag == "body-2-charts") && (chartPage.charts.length == 2)) {
        // make the div to display 2 charts visible
        element.style.display = "block";
        for (i = 0; i < chartPage.charts.length; i++) {
          const chart = chartPage.charts[i];
          chart["chartId"] = `chart_2_${i + 1}`;
        }
      } else if ((tag == "body-1-chart") && (chartPage.charts.length == 1)) {
        // make the div to display 1 chart visible
        element.style.display = "block";
        for (i = 0; i < chartPage.charts.length; i++) {
          const chart = chartPage.charts[i];
          chart["chartId"] = `chart_1_${i + 1}`;
        }
      } else {
        // make other chart div invisible
        element.style.display = "none";
      }
    }
  });

  // generate charts using chartFunction into the chartId tag
  chartPage.charts.forEach(entry => {
    entry.chartFunction(entry.chartId);
  });

}

/**
 * Load the controls HTML fragment into the target placeholder element.
 * @param {string} placeHolderId - The id of the element to fill with HTML.
 * @param {string} htmlFile - The path to the HTML fragment to load.
 * @returns {Promise<void>} Resolves when content has been loaded.
 */
export async function loadControlsHtml(placeHolderId, htmlFile) {
  await fetch(htmlFile)
    .then(r => r.text())
    .then(html => {
      document.getElementById(placeHolderId).innerHTML = html;
    })
}

/**
 * Register a callback to be invoked when either time slider changes.
 * Duplicate callbacks are ignored.
 * @param {Function} callBack - A callback function for slider updates.
 */
export function addTimeSliderCallBack(callBack) {
  if (callBackList.indexOf(callBack) == -1) {
    callBackList.push(callBack);
  }
}

/**
 * Get the current selected time unit labels for the chosen bucket.
 * @returns {string[]} An array with display units and identifier keys.
 */
export function getTimeUnits() {
  const timeBucket = document.querySelector('input[name="timeBucket"]:checked').value;
  if (timeBucket == "daily") {
    return ["Day", "day_date", "Daily"];
  } else if (timeBucket == "hourly") {
    return ["Hour", "hour_date", "Hourly"];
  } else if (timeBucket == "monthly") {
    return ["Month", "month_date", "Monthly"];
  } else {
    return ["Second", "time", "Seconds"];
  }
}

/**
 * Get the time labels for the current bucket selection.
 * @returns {string[]} The list of labels for the selected bucket.
 */
export function getTimeLabels() {
  const timeBucketElement = document.querySelector('input[name="timeBucket"]:checked');
  const timeBucket = timeBucketElement ? timeBucketElement.value : "daily";
  if (!csvData) return [];
  if (timeBucket == "daily") {
    return csvData["dailyLabels"];
  } else if (timeBucket == "hourly") {
    return csvData["hourlyLabels"];
  } else if (timeBucket == "monthly") {
    return csvData["monthlyLabels"];
  } else {
    return [];
  }
}

/**
 * Get the current slider start and end positions.
 * @returns {number[]} An array containing [startIndex, endIndex].
 */
export function getSliderPosition() {
  return [currentStartIndex, currentEndIndex];
}

/**
 * Get all loaded CSV rows for chart rendering.
 * @returns {Array<Object>} The rows loaded from the CSV data.
 */
export function getRows() {
  return csvData["rows"];
}

/**
 * Load the charts definition configuration from report_definitions.yaml.
 * @returns {Promise<Object>} containing a yaml object.
 * The returned yaml object has keys.
 *   id: The id of the entry in the definition file of selected entry.
 *   chartPage: The definition of the selected entry from the definition file.
 *   definedPages: A list of all the pages as {"name":"", "title":""}.
 */
async function loadChartDefinitions() {
  const reportDefintionsUrl = "report_definitions.yaml";
  const url = new URL(window.location.href);
  let pageName = url.searchParams.get("page");
  const definedPages = [];
  const response = await fetch(reportDefintionsUrl);
  if (!response.ok) {
    throw new Error(`Unable to load report definition file ${reportDefintionsUrl}: ${response.status} ${response.statusText}`);
  }
  const contents = await response.text();
  const chartsJson = jsyaml.load(contents);
  const chartsJsonKeys = Object.keys(chartsJson);
  if (chartsJsonKeys.length == 0) {
    throw new Error(`The ${reportDefintionsUrl} definition file is empty.`);
  }
  const firstKey = chartsJsonKeys[0];
  if (!pageName) pageName = firstKey;
  if (!chartsJson[pageName]) pageName = firstKey;
  const chartPage = chartsJson[pageName];
  let i;
  for (i = 0; i < chartPage.charts.length; i++) {
    let chart = chartPage.charts[i];
    const module = await import(`./${chart.js_file}`);
    if (!module) throw new Error(`No module '${chart.js_file}' found`);
    const chartFunction = module[chart.js_function];
    if (!chartFunction) throw new Error(`No function '${chart.js_function} in module '${chart.js_file}'`);
    chart["chartFunction"] = chartFunction;
    chart["chartId"] = `chart_${i + 1}`;
  }
  for (i = 0; i < chartsJsonKeys.length; i++) {
    const key = chartsJsonKeys[i];
    const entry = chartsJson[key];
    const title = entry["title"] ? entry["title"] : key;
    definedPages.push({ id: key, title: title });
  }
  const result = {
    id: pageName,
    chartPage: chartPage,
    definedPages: definedPages
  }
  return result;
}

/**
 * Initialize slider elements and attach event handlers.
 */
function intializeSliders() {
  const allLabels = getTimeLabels();
  startSlider = document.getElementById("startSlider");
  endSlider = document.getElementById("endSlider");
  startLabel = document.getElementById("startLabel");
  endLabel = document.getElementById("endLabel");
  statusElement = document.getElementById("status");

  if (!startSlider || !endSlider || !startLabel || !endLabel) {
    throw new Error('Unable to initialize chart controls: one or more element IDs are invalid.');
  }
  const [startIndex, endIndex] = getSliderInitialDateIndexes();
  currentStartIndex = startIndex;
  currentEndIndex = endIndex;

  startSlider.min = 0;
  startSlider.max = endIndex;
  endSlider.min = startIndex;
  endSlider.max = allLabels.length - 1;
  startSlider.value = currentStartIndex;
  endSlider.value = currentEndIndex;
  startSlider.addEventListener('input', () => updateTimeRange(true));
  endSlider.addEventListener('input', () => updateTimeRange(false));
  document.getElementById("dailyTimeBucket").addEventListener('input', () => updateTimeBucket());
  document.getElementById("hourlyTimeBucket").addEventListener('input', () => updateTimeBucket());
  document.getElementById("monthlyTimeBucket").addEventListener('input', () => updateTimeBucket());
}

function initializeTimeBucketOption() {
  const url = new URL(window.location.href);
  let timeUnits = url.searchParams.get("units");
  if (timeUnits) {
    const timeBucketLablels = ["hourlyTimeBucket", "dailyTimeBucket", "monthlyTimeBucket"];
    const bucketToUnitMap = { "hourlyTimeBucket": "hour", "dailyTimeBucket": "day", "monthlyTimeBucket": "month" };
    timeBucketLablels.forEach(bucket => {
      const id = bucketToUnitMap[bucket];
      const element = document.getElementById(bucket);
      if (element && id == timeUnits.toLowerCase()) {
        element.checked = true;
      }
    })
  }
}
function getSliderInitialDateIndexes() {
  const url = new URL(window.location.href);
  let queryStart = url.searchParams.get("start");
  let queryEnd = url.searchParams.get("end");
  let paramLogHash = url.searchParams.get("log_id");
  const logHash = createCsvFileHash();
  const timeLabels = getTimeLabels();
  if (queryStart && queryEnd && paramLogHash == logHash) {
    const queryStartIndex = timeLabels.indexOf(queryStart);
    const queryEndIndex = timeLabels.indexOf(queryEnd);
    const startIndex = queryStartIndex >= 0 ? queryStartIndex : 0;
    const endIndex = queryEndIndex >= 0 ? queryEndIndex : table_labels.length - 1;
    return [startIndex, endIndex];
  } else {
    return [0, timeLabels.length - 1];
  }
}

function hash8(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
  }
  return hash & 0xFF; // Ensure it stays within 8 bits (0-255)
}
function createCsvFileHash() {
  if (!csvData) return "";
  const rows = csvData["rows"];
  if (rows.length == 0) return "";
  const checksum = hash8(Object.keys(rows[0]).join(","));
  return checksum;
}

/**
 * Update the current slider selection and refresh labels/status.
 * @param {boolean} isStartChanged - Whether the start slider triggered the update.
 */
function updateTimeRange(isStartChanged) {
  const newStart = parseInt(startSlider.value, 10);
  const newEnd = parseInt(endSlider.value, 10);
  const allLabels = getTimeLabels();

  if (isStartChanged) {
    endSlider.min = newStart;
    currentStartIndex = newStart;
    startSlider.value = newStart;
  } else {
    startSlider.max = newEnd;
    currentEndIndex = newEnd;
    endSlider.value = newEnd;
  }

  updateSliderLabels();
  callBackList.forEach(callBack => {
    callBack();
  });
  const [units] = getTimeUnits();
  if (statusElement) {
    statusElement.textContent =
      `Displaying ${currentEndIndex - currentStartIndex + 1} ${units}s from ${allLabels[currentStartIndex]} to ${allLabels[currentEndIndex]}.`;
  }
}

/**
 * Update because the time bucket changed.
 */
function updateTimeBucket() {
  const allLabels = getTimeLabels();
  currentStartIndex = 0;
  currentEndIndex = allLabels.length - 1;
  startSlider.value = 0;
  endSlider.max = allLabels.length - 1;
  endSlider.value = allLabels.length - 1;
  startSlider.max = allLabels.length - 1;
  updateTimeRange(false);
  updateTimeRange(true);
  updateSliderLabels();
}

/**
 * Refresh the start/end label text based on current slider positions.
 */
function updateSliderLabels() {
  const [units] = getTimeUnits();
  const allLabels = getTimeLabels();
  if (allLabels && allLabels.length > 0 && startLabel && endLabel) {
    startLabel.textContent = allLabels[currentStartIndex] || '—';
    endLabel.textContent = allLabels[currentEndIndex] || '—';
    document.getElementById("startTimeUnits").innerHTML = units;
    document.getElementById("endTimeUnits").innerHTML = units;
  }
}

/**
 * Initialize the page heading using the title from the chartPage.
 * @param {string} definitionId - is the key of selected page from definition file.
 * @param {object} chartPage - the selected chart page from chart_pages.json.
 * @param {object[]} definedPages - list of availble charts as {id:,title:}.
 * Set the title in the heading using the title from the chartPage.
 * Populate the options for new charts using definedPages.
 */
function initializeHeading(definitionId, chartPage, definedPages) {
  // Set the chart page title in the heading
  const chartTitle = chartPage.title;
  const chartTitleElement = document.getElementById("chart_title");
  if (chartTitleElement) chartTitleElement.innerHTML = chartTitle;

  // Add the option values for the select_chart drop down using definedPages.
  let i;
  const selectElement = document.getElementById("select_chart");
  if (selectElement) {
    for (i = 0; i < definedPages.length; i++) {
      var entry = definedPages[i];
      var element = document.createElement("option")
      element.textContent = entry["title"];
      element.value = entry["id"];
      if (entry["id"] == definitionId) {
        element.selected = true;
      }
      selectElement.appendChild(element);
    }

    // Create an event handle to respond to changes to the drop down.
    selectElement.addEventListener("change", changeSelectedChart);
  }
}

/**
 * Respond to a change event for the select_chart select tag.
 * @param {object} event - event passed to the handler.
 * Change the browser current window to use the ?page= for new chart.
 */
function changeSelectedChart(event) {
  const selectedValue = event.target.value;
  const [units] = getTimeUnits();
  const [currentStartIndex, currentEndIndex] = getSliderPosition();
  const timeLabels = getTimeLabels();
  const timeRangeRows = timeLabels.slice(currentStartIndex, currentEndIndex + 1);
  const startDate = timeRangeRows[0];
  const endDate = timeRangeRows[timeRangeRows.length - 1];

  const logHash = createCsvFileHash();
  const url = `.?page=${selectedValue}&start=${startDate}&end=${endDate}&units=${units}&log_id=${logHash}`;

  window.location = url;
}

/**
 * Return true if the row is successful.
 * @param {Object} row - One row from log file. 
 */
export function isSuccessRow(row) {
  return row["status"] == "success";
}

/**
 * Return true if the user in the row is a testing user.
 * @param {Object} row - One row from log file. 
 */
export function isTestingUser(row) {
  const user_id = row["user_id"];
  if (["hf.test.public", "hf.test.private", "wh3248", "ad9465", "luet.princeton", "georgios.artavanis"].includes(user_id)) {
    return true;
  } else {
    return false;
  }
}

/**
 * Return rows within the date range selected by the slider.
 * @param {Boolean} status - flat to return success/failed rows.
 * If status is true only return success rows.
 * If status is false only return failed rows.
 * If status is not provided or undefined return all rows.
 */
export function getRowsInDateRange(status) {
  const rows = getRows();
  const [currentStartIndex, currentEndIndex] = getSliderPosition();
  const timeLabels = getTimeLabels();
  const timeRangeRows = timeLabels.slice(currentStartIndex, currentEndIndex + 1);
  const startDate = timeRangeRows[0];
  const endDate = timeRangeRows[timeRangeRows.length - 1];
  // Use the filter() method to create a new array with matching rows
  const [units, time_column] = getTimeUnits()
  const filteredRows = rows.filter(row => {
    const rowDate = row[time_column];

    // Compare dates using comparison operators.
    // JavaScript internally converts Date objects to their millisecond timestamps for comparison.
    if (status == true) {
      return isSuccessRow(row) && rowDate >= startDate && rowDate <= endDate;
    } else if (status == false) {
      return !isSuccessRow(row) && rowDate >= startDate && rowDate <= endDate;
    } else {
      return rowDate >= startDate && rowDate <= endDate;
    }
  });
  return filteredRows;
}