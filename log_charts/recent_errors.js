/*
  This module implements a chart to display top 10 recent errors per time period.
*/
import { addTimeSliderCallBack, getRowsInDateRange, isSuccessRow } from './controls_handler.js';

let chartId;

/**
 * Initialize the errorsTop10Report chart.
 *
 * @param {string|HTMLElement} chartIdArg - The target DOM element id or element for Plotly rendering.
 */
export function errorsTop10Report(chartIdArg) {
  chartId = chartIdArg;
  addTimeSliderCallBack(renderReport);

  renderReport();
}

/**
 * Render the recent errors chart using the current slider range.
 */
function renderReport() {
  const rows = getRowsInDateRange();
  if (!rows || rows.length === 0) {
    updateReportHtml('<div class="status">No rows available for report.</div>');
    return;
  }

  const userMap = new Map();
  const timeMap = new Map();
  const countMap = new Map();
  const actionMap = new Map();
  rows.forEach(row => {
    if (!isSuccessRow(row)) {
      const message = row["exception"];
      const rowTime = row["time"];
      const userId = row["user_id"];
      const action = row["action"];
      countMap.set(message, (countMap.get(message) || 0) + 1);
      userMap.set(message, userId);
      timeMap.set(message, rowTime);
      actionMap.set(message, action);
    }
  });
  const errorRows = [];
  const rowKeys = countMap.keys();
  rowKeys.forEach(key => {
    const messageCount = countMap.get(key);
    const userId = userMap.get(key);
    const rowTime = timeMap.get(key);
    const action = actionMap.get(key);
    const entry = { message_time: rowTime, user_id: userId, action: action, row_count: messageCount, message: key };
    errorRows.push(entry);
  })

  const topRows = [...errorRows]
    .sort((a, b) => parseInt(b.message_time) - parseInt(a.message_time))
    .slice(0, 10);
  const tableHeaders = ['Latest Time', 'User', 'Action', 'Count', 'Message'];
  const tableColumns = ['message_time', 'user_id', 'action', 'row_count', 'message'];
  const tableRows = topRows
    .map(row => `
      <tr>
        ${tableColumns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}
      </tr>`)
    .join('');

  const tableHtml = `
    <div class="report-content">
      <h3>Top 10 Errors</h3>
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
