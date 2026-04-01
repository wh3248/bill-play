import { addTimeSliderCallBack, getRowsInDateRange } from './controls_handler.js';

let chartId;

/**
 * Initialize the Top 10 duration report.
 *
 * @param {string} chartIdArg - The DOM element id where the report should be rendered.
 */
export function top10DurationReport(chartIdArg) {
    chartId = chartIdArg;
    addTimeSliderCallBack(renderReport);

    renderReport();
}

/**
 * Render the Top 10 duration report.
 */
function renderReport() {
    const rows = getRowsInDateRange(true);
    if (!rows || rows.length === 0) {
        updateReportHtml('<div class="status">No rows available for report.</div>');
        return;
    }

    const topRows = [...rows]
        .sort((a, b) => parseFloat(b.duration) - parseFloat(a.duration))
        .slice(0, 10);
    const tableHeaders = ['Time', 'User', 'Duration (s)', 'Status', 'Kbytes'];
    const tableColumns = ['time', 'user_id', 'duration', 'status', 'bytes'];
    const tableRows = topRows
        .map(row => `
      <tr>
        ${tableColumns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}
      </tr>`)
        .join('');

    const tableHtml = `
    <div class="report-content">
      <h3>Top 10 Duration Requests</h3>
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
    /**
     * Update the report container HTML.
     *
     * @param {string} html - The rendered HTML to insert into the report container.
     */
    const element = document.getElementById(chartId);
    if (!element) {
        throw new Error(`Element with ID "${chartId}" not found.`);
    }
    element.innerHTML = html;
}
