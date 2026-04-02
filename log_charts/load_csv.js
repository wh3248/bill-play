/*
 * This file contains an exported function loadCsv to load the log information from server.
*/

/**
 * Fetch a CSV log file from the server, parse it, and return the parsed rows.
 * @param {string} csvPath - The URL path to the CSV file.
 * @returns {Promise<{rows: object[], dailyLabels: string[], hourlyLabels: string[]}>>} Promise resolving to CSV data.
 *   The returned object includes rows with added day_date and hour_date columns,
 *   plus unique dailyLabels and hourlyLabels.
 */
export async function loadCsv(csvPath) {
  const response = await fetch(csvPath);
  if (!response.ok) {
    throw new Error(`Unable to load CSV log file '${csvPath}': ${response.status} ${response.statusText}`);
  }

  const text = await response.text();
  const result = Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
    dynamicTyping: false,
  });

  if (result.errors && result.errors.length) {
    console.log('CSV parse warnings/errors:', result.errors);
  }

  if (!result.data) {
    throw new Error('CSV parse returned no data.');
  }

  const [monthlyLabels, dailyLabels, hourlyLabels] = createMonthDayHourColumns(result.data);
  const csvData = {
    rows: result.data,
    dailyLabels: dailyLabels,
    hourlyLabels: hourlyLabels,
    monthlyLabels : monthlyLabels
  };
  return csvData;
}

/**
 * Add three columns, "month_date", "day_date" and "hour_date", to each row and collect labels.
 * @param {Array<object>} rows - Parsed CSV rows with at least a time field.
 * @returns {[string[], string[], string[]]} A tuple containing [monthlyLabels, dailyLabels, hourlyLabels].
 *   dailyLabels contains unique day_date values and hourlyLabels contains unique hour_date values.
 */
function createMonthDayHourColumns(rows) {
  const dailyLabels = [];
  const hourlyLabels = [];
  const monthlyLabels = [];
  rows.forEach(row => {
    const timeValue = row.time || row['time'];
    const date = parseCsvTime(timeValue);
    if (!date) {
      return;
    }

    date.setMinutes(0, 0, 0);
    const hourKey = formatHourLabel(date);
    row["hour_date"] = hourKey;
    if (hourlyLabels.indexOf(hourKey) == -1) {
      hourlyLabels.push(hourKey);
    }

    date.setHours(0, 0, 0, 0);
    const dayKey = formatDayLabel(date);
    row["day_date"] = dayKey;
    if (dailyLabels.indexOf(dayKey) == -1) {
      dailyLabels.push(dayKey);
    }

    const monthKey = formatMonthLabel(date);
    row["month_date"] = monthKey;
    if (monthlyLabels.indexOf(monthKey) == -1) {
      monthlyLabels.push(monthKey);
    }
  });
  return ([monthlyLabels, dailyLabels, hourlyLabels]);
}


/**
 * Format a Date object as an hourly label string.
 * @param {Date} date
 * @returns {string}
 */
function formatHourLabel(date) {
  return date.toISOString().slice(0, 13).replace('T', ' ') + ':00';
}

/**
 * Format a Date object as a day label string.
 * @param {Date} date
 * @returns {string}
 */
function formatDayLabel(date) {
  if (!(date instanceof Date) || isNaN(date)) {
    return '';
  }
  return date.toISOString().slice(0, 10);
}

/**
 * Format a Date object as a month label string.
 * @param {Date} date
 * @returns {string}
 */
function formatMonthLabel(date) {
  if (!(date instanceof Date) || isNaN(date)) {
    return '';
  }
  return date.toISOString().slice(0, 7);
}

/**
 * Parse a CSV time value into a Date object.
 * @param {string} value - The time string to parse.
 * @returns {Date|null} The parsed Date or null if the value is invalid.
 */
function parseCsvTime(value) {
  if (!value) {
    return null;
  }
  const normalized = value.trim().replace(/\s+/g, ' ');
  const parsed = new Date(normalized);
  return isNaN(parsed) ? null : parsed;
}
