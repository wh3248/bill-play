/*
  This module implements recent user signups report.
*/
import { addTimeSliderCallBack, getRowsInDateRange, isSuccessRow } from './controls_handler.js';

let chartId;

/**
 * Initialize the recent_user_signup report.
 *
 * @param {string|HTMLElement} chartIdArg - The target DOM element id or element for Plotly rendering.
 */
export function recentUserSignups(chartIdArg) {
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
  const topRows = [...rows]
  .sort((a, b) => b.time.localeCompare(a.time))
    .slice(0, 10);
  const tableHeaders = ['Signup Time', 'User', 'Email', 'First Name', 'Last Name', "Org Type", "Affiliation"];
  const tableColumns = ['time', 'user_id', 'email', 'first_name', 'last_name', 'organization_type','affiliation'];
  const tableRows = topRows
    .map(row => `
      <tr>
        ${tableColumns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}
      </tr>`)
    .join('');

  const tableHtml = `
    <div class="report-content">
      <h3>Most Recent 10 Users</h3>
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
