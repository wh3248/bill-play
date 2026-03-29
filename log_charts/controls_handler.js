/*
  This module contains function to handle events from the slider and bucket size controls
  in the HTML file. This also holds the loaded rows from the CSV file and provides information
  and the slider positions and data back to the various charts.
 */

let currentStartIndex = 0;
let currentEndIndex = 0;
let startSlider;
let endSlider;
let startLabel;
let endLabel;
let statusElement;

let sliderState = {};
let callBackList = [];
let timeBucket = "hourly";

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
  const timeBucket = document.querySelector('input[name="timeBucket"]:checked').value;
  if (timeBucket == "daily") {
    return sliderState["dailyLabels"];
  } else {
    return sliderState["hourlyLabels"];
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
  return sliderState["rows"];
}

export function timeSliderHandler(chartViewConfig, dailyLabels, hourlyLabels, rows) {
  sliderState["dailyLabels"] = dailyLabels;
  sliderState["hourlyLabels"] = hourlyLabels;
  sliderState["rows"] = rows;
  const allLabels = getTimeLabels();
  startSlider = document.getElementById(chartViewConfig.startSliderId);
  endSlider = document.getElementById(chartViewConfig.endSliderId);
  startLabel = document.getElementById(chartViewConfig.startLabelId);
  endLabel = document.getElementById(chartViewConfig.endLabelId);
  statusElement = document.getElementById(chartViewConfig.statusId);

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
  const allLabels = sliderState["hourlyLabels"];
  startLabel.textContent = allLabels[currentStartIndex] || '—';
  endLabel.textContent = allLabels[currentEndIndex] || '—';
}
