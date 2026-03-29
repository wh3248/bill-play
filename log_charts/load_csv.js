/*
 * This file contains an exported function loadCsv to load the log information from server.
*/

/* 
  Add two columns "day_date" and "hour_date" to each row.
  Parameters:
    rows:   is a list of rows, where each row is a map of column name to value from log file.
  Returns:
    An array [dailyLabels, hourlyLabels]
  The new day_date column is the time column of the row formatted as day.
  The new hour_date column is the time column of the row formatted as an hour.

  The dailyLabels is a list unique day_date values.
  The hourlyLabels is a list of unique hour_date values.
*/
function createDayHourColumns(rows) {
  const dailyLabels = [];
  const hourlyLabels = [];
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
  });
  return ([dailyLabels, hourlyLabels]);
}

/* 
 * Fetch a csv log file from the server, parse it and return the rows.
 * Parameters:
 *  csvPath:  The URL path to the csv file.
 * Returns a map with keys: rows, dailyLabels, hourlyLabels.
 * The rows are all rows in the csv file with day_date and hour_date added.
 * The dailyLabels is a list of unique day labels.
 * The hourlyLabels is a list of unique hour labels.
 */
export async function loadCsv(csvPath) {
  const response = await fetch(csvPath);
  if (!response.ok) {
    throw new Error(`Unable to load CSV file: ${response.status} ${response.statusText}`);
  }

  const text = await response.text();
  const result = Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
    dynamicTyping: false,
  });

  if (result.errors && result.errors.length) {
    console.warn('CSV parse warnings/errors:', result.errors);
  }

  if (!result.data) {
    throw new Error('CSV parse returned no data.');
  }

  const [dailyLabels, hourlyLabels] = createDayHourColumns(result.data);
  const bucketResults = {
    rows: result.data,
    dailyLabels: dailyLabels,
    hourlyLabels: hourlyLabels,
  };
  return bucketResults;
}

function formatHourLabel(date) {
  return date.toISOString().slice(0, 13).replace('T', ' ') + ':00';
}

function formatDayLabel(date) {
  if (!(date instanceof Date) || isNaN(date)) {
    return '';
  }
  return date.toISOString().slice(0, 10);
}

function parseCsvTime(value) {
  if (!value) {
    return null;
  }
  const normalized = value.trim().replace(/\s+/g, ' ');
  const parsed = new Date(normalized);
  return isNaN(parsed) ? null : parsed;
}
