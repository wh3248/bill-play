import { addTimeSliderCallBack, getRowsInDateRange, getTimeUnits, isSuccessRow } from './controls_handler.js';

let chartId;

export function actionsTop10Report(chartIdArg) {
  chartId = chartIdArg;
  addTimeSliderCallBack(renderReport);

  renderReport();
}

function renderReport() {
  const rows = getRowsInDateRange();
  if (!rows || rows.length === 0) {
    updateReportHtml('<div class="status">No rows available for report.</div>');
    return;
  }

  const [units, time_column] = getTimeUnits();

  // Create a map with a key for user_id/time to count requests by that key
  const requestsMap = new Map();
  const successRequestsMap = new Map();
  rows.forEach(row => {
    const timeKey = row[time_column]
    const user_id = row["user_id"];
    const action = row["action"];
    const rowKey = `${timeKey}#${user_id}#${action}`;
    requestsMap.set(rowKey, (requestsMap.get(rowKey) || 0) + 1);
    if (isSuccessRow(row)) {
      successRequestsMap.set(rowKey, (successRequestsMap.get(rowKey) || 0) + 1);
    }
  });

  // Create a reportRows array for the rows for the chart table
  const reportRows = [];
  const mapKeys = requestsMap.keys();
  mapKeys.forEach(key => {
    const [timeKey, user_id, action] = key.split("#");
    const keyCount = requestsMap.get(key);
    const successKeyCount = successRequestsMap.get(key);
    const entry = { user_id: user_id, time_key: timeKey, action: action, request_count: keyCount, success_count: successKeyCount };
    reportRows.push(entry)
  })

  const topRows = [...reportRows]
    .sort((a, b) => parseInt(b.request_count) - parseInt(a.request_count))
    .slice(0, 10);
  const tableHeaders = ['Time', 'User', 'Action', '# Requests', '# Success'];
  const tableColumns = ['time_key', 'user_id', 'action', 'request_count', 'success_count'];
  const tableRows = topRows
    .map(row => `
      <tr>
        ${tableColumns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}
      </tr>`)
    .join('');

  const tableHtml = `
    <div class="report-content">
      <h3>Top 10 # Actions</h3>
      <table class="report-table">
        <thead>
          <tr>
            ${tableHeaders.map(col => `<th>${col}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${tableRows}
        </tbody>
      </table>
    </div>`;

  updateReportHtml(tableHtml);
}

function updateReportHtml(html) {
  const element = document.getElementById(chartId);
  if (!element) {
    throw new Error(`Element with ID "${chartId}" not found.`);
  }
  element.innerHTML = html;
}
