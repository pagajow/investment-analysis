import $ from "jquery";
import { type } from "os";
import Plotly from 'plotly.js-dist';
import _ from 'lodash';

function plotChart(containerId, data, title="", xLabel="X", yLabel="Y", addLayout={}, margin={l: 30, r: 30, t: 30, b: 30}) {
    let layout = {};
    if (title !== null && title !== undefined)  {
        layout.title = { text: title };
    }
    if (xLabel !== null && xLabel !== undefined)  {
        layout.xaxis = {title: { text: xLabel }};
    }
    if (yLabel !== null && yLabel !== undefined)  {
        layout.yaxis = {title: { text: yLabel }};
    }
    layout = _.merge(layout, margin);
    layout = _.merge(layout, addLayout);
    const config = { staticPlot: true, displayModeBar: false };
    Plotly.newPlot(containerId, data, layout, config);
}


export function plotLineChart(containerId, data, title="", xLabel="X", yLabel="Y", addLayout={}) {
    // const data = [{x: [1, 2, ..., x], y: [1, 2, ..., y], name: 'name' }];
    for (const d of data) {
        d.type = 'line';
    }
    plotChart(containerId, data, title, xLabel, yLabel, addLayout);
}

export function plotBarChart(containerId, data, title="", xLabel="X", yLabel="Y", addLayout={}) {
    // const data = [{x: [1, 2, ..., x], y: [1, 2, ..., y], name: 'name' }];
    for (const d of data) {
        d.type = 'bar';
    }
    plotChart(containerId, data, title, xLabel, yLabel, addLayout);
}

export function plotPieChart(containerId, data, title="", xLabel="X", yLabel="Y", addLayout={}) {
    // const data = [{x: [1, 2, ..., x], y: [1, 2, ..., y], name: 'name' }];
    for (const d of data) {
        d.type = 'pie';
    }
    plotChart(containerId, data, title, xLabel, yLabel, addLayout);
}

export function plotScatterChart(containerId, data, title="", xLabel="X", yLabel="Y", addLayout={}, size=12) {
    // const data = [{x: [1, 2, ..., x], y: [1, 2, ..., y], name: 'name' }];
    for (const d of data) {
        d.type = 'scatter';
        d.mode = 'markers';
        d.marker = { size: size };
    }
    plotChart(containerId, data, title, xLabel, yLabel, addLayout);
}

export function plotHeatmapChart(containerId, data, title="", xLabel="X", yLabel="Y", addLayout={},  showscale=false, decimalPlaces=2) {
    // const data = [{z: [[1,2,3], [4,5,6], [7,8,9]], x: [1, 2, 3], y: [1, 2, 3]}];
    for (const d of data) {
        const roundedData = d.z.map(row => row.map(value => value.toFixed(decimalPlaces)));
        d.type = 'heatmap';
        d.colorscale = "Viridis"; 
        d.showscale = showscale;
        d.text = roundedData;
        d.hoverinfo = 'text';
    }
    plotChart(containerId, data, title, xLabel, yLabel, addLayout);
}
