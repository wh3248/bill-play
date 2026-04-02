/*
  This module implements a chart to display total number of user signup at time bucket.
*/

import { addTimeSliderCallBack, getSliderPosition, getRows, getTimeLabels, getTimeUnits, isTestingUser } from './controls_handler.js';

let chartId;

/**
 * Initialize the total_users_per_time chart.
 *
 * @param {string|HTMLElement} chartIdArg - The target DOM element id or element for Plotly rendering.
 */
export function total_users_per_time(chartIdArg) {
    chartId = chartIdArg;
    addTimeSliderCallBack(renderChart);
    renderChart();
}

/**
 * Render the total_users_per_time chart using the current slider range.
 */
function renderChart() {
    const [units, time_column] = getTimeUnits();
    const timeLabels = getTimeLabels();
    const [currentStartIndex, currentEndIndex] = getSliderPosition();

    // Slice the timelabel for the the slider start/end index
    const slicedTimeLabels = timeLabels.slice(currentStartIndex, currentEndIndex + 1);


    let totalUsers = 0;
    const rows = getRows();
    console.log("USER ROWS", rows.length);
    const totalUsersCountMap = new Map();
    rows.forEach(row => {
        totalUsers = totalUsers + 1;
        const timeKey = row[time_column];
        totalUsersCountMap.set(timeKey, totalUsers);
    });

    // Compute Y values for each timeLabel
    const reportRows = [];
    slicedTimeLabels.forEach(timeLabel => {
        reportRows.push(totalUsersCountMap.get(timeLabel) || 0);
    });
    console.log("REPORT ROWS", reportRows.length);

    // Draw the chart in the chartId HTML element.
    Plotly.react(chartId, [
        {
            x: slicedTimeLabels,
            y: reportRows,
            type: 'scatter',
            mode: 'lines+markers',
            marker: { color: '#fca311', size: 6 },
            line: { shape: 'linear', color: '#fca311', width: 3 },
            hovertemplate: '%{x}<br>Requests: %{y}<extra></extra>',
        },
    ], {
        title: `# Signed Up Users Over Time`,
        xaxis: {
            title: units,
            tickangle: -45,
            automargin: true,
            type: 'date',
            tickformat: units === 'Day' ? '%Y-%m-%d' : undefined,
        },
        yaxis: {
            title: `# Total Number of Users`,
            rangemode: 'tozero',
        },
        margin: { t: 35, r: 24, l: 60, b: 5 },
        paper_bgcolor: '#f2f4f8',
        plot_bgcolor: '#ffffff',
    }, { responsive: true });
}

