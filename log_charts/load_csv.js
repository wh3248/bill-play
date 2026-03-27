import { createHourlyBuckets } from './requests_per_hour_chart.js';

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

  const bucketed = createHourlyBuckets(result.data);
  return {
    labels: bucketed.labels,
    values: bucketed.values,
    rowCount: result.data.length,
  };
}

