import { addTimeSliderCallBack, getRowsInDateRange } from './controls_handler.js';

let chartId;

export function top10BytesReport(chartIdArg) {
    chartId = chartIdArg;
    addTimeSliderCallBack(renderReport);

    renderReport();
}

function renderReport() {
    const rows = getRowsInDateRange(true);
    if (!rows || rows.length === 0) {
        updateReportHtml('<div class="status">No rows available for report.</div>');
        return;
    }

    const topRows = [...rows]
        .sort((a, b) => parseFloat(b.bytes) - parseFloat(a.bytes))
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
      <h3>Top 10 Bytes Requests</h3>
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
