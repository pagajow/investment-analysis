import {drawChart, addSummmaryCard} from './fincharts'
import $ from 'jquery';
import { getApiUrl } from '../utils'


let reportData = null;
let activeTab = 0;

init()

function init() {
    window.addEventListener("resize", () => {
        drawDashboard(reportData);
    })

    window.addEventListener("ImportCompleted", event => {
        const company_id = $('#fin-dashboard').attr('data-company-id');
        const url = `api/company/${company_id}/analize-financial-data/`;
        getFindata(getApiUrl(url)).then(data => {
            console.log(data)
            reportData = data;
            drawDashboard(reportData);
        })
    })

    document.getElementById('file-upload-form').addEventListener('submit', function(event) {
        const fileInput = document.getElementById('file-input');
        if (!fileInput.files.length) {
            event.preventDefault(); // Zatrzymaj wysyłanie formularza
            alert('Please select a file before submitting.');
        }
    });

    $("#download_financial_data").on("click", downloadFinData);
}

function downloadFinData(event){
    downloadTableAsCSV("financial-data-table", 'fin-data.csv')
}

function downloadTableAsCSV(tableId, filename) {
    const table = document.querySelector(`#${tableId}`);
    const headers = Array.from(table.querySelectorAll("thead th"));
    const dataRows = Array.from(table.querySelectorAll("tbody tr"));

    // Pobierz nagłówki z atrybutem `data-field`
    const headerFields = headers.map(header => header.getAttribute("data-field") || header.textContent.trim());

    // Pobierz dane z wierszy
    const rows = dataRows.map(row => {
        return Array.from(row.querySelectorAll("td input, td")).map(cell => {
            return cell.value ? cell.value.trim() : cell.textContent.trim();
        });
    });

    // Zbuduj CSV
    const csvContent = [
        headerFields.join(","), // Nagłówki
        ...rows.map(row => row.join(",")) // Dane
    ].join("\n");

    // Utwórz plik Blob z zawartością CSV
    const blob = new Blob([csvContent], { type: "text/csv" });

    // Utwórz tymczasowy link do pobrania
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.style.display = "none";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


async function getFindata(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error during loading data:', error);
        return null;
    }
}




function drawDashboard(data){
    if (!data) {
        return;
    }
    
    const findata = data["financial_data"]
    const big5Data = data.analysis["big5"];
    const healthData = data.analysis["health"];
    const dcfData = data.analysis["dcf"];

    const dashboardID = "fin-dashboard";
    const $finDashboard = $(`#${dashboardID}`);
    $finDashboard.empty();

    const tabsContainer = $('<div>', {id: "tabs-container", class: "tabs-bar"})
    const tabBodiesContainer = $('<div>', {id: "tabbodies-container", class: "tabs-container"})
    $finDashboard.append(tabsContainer)
    $finDashboard.append(tabBodiesContainer)

    function onTabClick(e){
        const $clickedTab = $(e.target); 
        activeTab = $clickedTab.index(); 
    
        $clickedTab.siblings().removeClass("active-tab");
        $clickedTab.addClass("active-tab");
    
        $(".tab-body").addClass("hidden");
        $(".tab-body").eq(activeTab).removeClass("hidden");
        drawDashboard(data)
    }

    const tabNames = ["overview", "big5", "health", "other"];
    tabNames.forEach((name, index) => {
        tabsContainer.append($('<button>', {
            id: `tab-${name}`,
            class: "tab-btn" + (index===activeTab ? " active-tab" : ""),
            "data-tabname": name,
        }).text(name).on("click", onTabClick))
        tabBodiesContainer.append($('<div>', {
            id: `tab-body-${name}`,
            class: "tab-body" + (index===activeTab ? "" : " hidden"),
            "data-tabname": name,
        }))
    });

    const currentTabBody = tabBodiesContainer.children().eq(activeTab)
    if (activeTab == 0) {
        drawTabOverview(currentTabBody, big5Data, healthData, dcfData);
    }
    if (activeTab == 1) {
        drawTabBig5(currentTabBody, findata);
    }
    if (activeTab == 2) {
        drawTabHealth(currentTabBody, findata);
    }
    if (activeTab == 3) {
        drawTabOther(currentTabBody, findata);
    }

}

function drawTabOverview(parent, big5Data, healthData, dcfData){
    addSummmaryCard(parent, "summary", big5Data, healthData, dcfData)
}
function drawTabBig5(parent, findata){
    const $chartContainer = $('<div>', { class: "chart-container" });
    $(parent).append($chartContainer);

    const $ROI = $('<div>', { id: "ROI", class: "fin-element fin-chart" });
    $($chartContainer).append($ROI);
    const $revenue = $('<div>', { id: "revenue", class: "fin-element fin-chart" });
    $($chartContainer).append($revenue);
    const $EPS = $('<div>', { id: "EPS", class: "fin-element fin-chart" });
    $($chartContainer).append($EPS);
    const $BVPS = $('<div>', { id: "BVPS", class: "fin-element fin-chart" });
    $($chartContainer).append($BVPS);
    const $cash = $('<div>', { id: "cash", class: "fin-element fin-chart" });
    $($chartContainer).append($cash);

    drawChart($ROI, findata, "year", ["ROI"], [{ value: 10, color: "red", label: "Min" },])
    drawChart($revenue, findata, "year", ["revenue"])
    drawChart($EPS, findata, "year", ["EPS"])
    drawChart($BVPS, findata, "year", ["BVPS"])
    drawChart($cash, findata, "year", ["cash"])
}
function drawTabHealth(parent, findata){
    const $chartContainer = $('<div>', {
        class: "chart-container"
    });
    $(parent).append($chartContainer);
    
    const $cur_ratio = $('<div>', { id: "cur_ratio", class: "fin-element fin-chart" });
    $($chartContainer).append($cur_ratio);
    const $debt_to_equity = $('<div>', { id: "debt_to_equity", class: "fin-element fin-chart" });
    $($chartContainer).append($debt_to_equity);

    drawChart($cur_ratio, findata, "year", ["cur_ratio"])
    drawChart($debt_to_equity, findata, "year", ["debt_to_equity"])
}
function drawTabOther(parent, findata){
    const $chartContainer = $('<div>', {
        class: "chart-container"
    });
    $(parent).append($chartContainer);
    
    const $chart1 = $('<div>', { id: "chart1", class: "fin-element fin-chart" });
    $($chartContainer).append($chart1);
    const $chart2 = $('<div>', { id: "chart2", class: "fin-element fin-chart" });
    $($chartContainer).append($chart2);
    const $chart3 = $('<div>', { id: "chart3", class: "fin-element fin-chart" });
    $($chartContainer).append($chart3);
    const $chart4 = $('<div>', { id: "chart4", class: "fin-element fin-chart" });
    $($chartContainer).append($chart4);
    const $chart5 = $('<div>', { id: "chart5", class: "fin-element fin-chart" });
    $($chartContainer).append($chart5);

    drawChart($chart1, findata, "year", ["revenue", "net_income"])
    drawChart($chart2, findata, "year", ["total_assets", "ncur_assets", "cur_assets", "cash"])
    drawChart($chart3, findata, "year", ["total_liabilities", "ncur_liabilities", "cur_liabilities", "equity"])
    drawChart($chart4, findata, "year", ["net_income", "dividends", "buybacks"])
    drawChart($chart5, findata, "year", ["FCF"])
}



export const fd = {
    "drawDashboard": drawDashboard,
}