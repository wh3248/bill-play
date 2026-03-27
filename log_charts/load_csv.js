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

function createHourlyBuckets(rows) {
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

function createDailyBuckets(rows) {
  const counts = new Map();
  let minDate = null;
  let maxDate = null;

  rows.forEach(row => {
    const timeValue = row.time || row['time'];
    const date = parseCsvTime(timeValue);
    if (!date) {
      return;
    }

    date.setHours(0, 0, 0, 0);
    const dayKey = formatDayLabel(date);
    counts.set(dayKey, (counts.get(dayKey) || 0) + 1);

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
    const label = formatDayLabel(cursor);
    labels.push(label);
    values.push(counts.get(label) || 0);
    cursor.setDate(cursor.getDate() + 1);
  }

  return { labels, values };
}

export async function loadCsv(csvPath, dailyHourly) {
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

  const bucketed = dailyHourly == "daily" ? createDailyBuckets(result.data) : createHourlyBuckets(result.data);
  const bucketResults = {
    labels: bucketed.labels,
    values: bucketed.values,
    rowCount: result.data.length,
  };
  return bucketResults;
}

