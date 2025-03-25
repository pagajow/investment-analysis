import $ from 'jquery';
import { plotLineChart } from './charts';
import { showModal } from '../../utils';

let reportData = null;
let dcf_valuations = [];

let activeTab = 0;

const TAB_NAMES = ["filters", "dcf", "data"];
let company_id = null;

init()

function init() {
    window.addEventListener("resize", () => {
        drawDashboard();
    })

    window.addEventListener("ImportCompleted", event => {
        company_id = $('#fin-dashboard').attr('data-company-id');
        getFindata(company_id).then(data => {
            console.log(data)
            reportData = data;
            drawDashboard();
        })
    })

    document.getElementById('file-upload-form').addEventListener('submit', function(event) {
        const fileInput = document.getElementById('file-input');
        if (!fileInput.files.length) {
            event.preventDefault(); 
            alert('Please select a file before submitting.');
        }
    });

    $("#download_financial_data").on("click", downloadFinData);
}

async function downloadFinData(event) {
    try {
        const url = `/api/company/${company_id}/download-financial-data/`
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        if (data["status"] === "success") {
            const data_csv = data["financial_data"]
            const blob = new Blob([data_csv], { type: "text/csv" });

            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "financial_data.csv";  
            link.style.display = "none"; 

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else if (data["status"] === "error") {
            console.error(`Loading data failed: ${data["status"]}\n${data["details"]} `);
        } else {
            console.error(`Error during loading data: uknown response ${data["status"]}\n${data}`);
        }
    } catch (error) {
        console.error('Error during loading data:', error);
    }

}

async function getFindata(company_id) {
    try {
        const url = `/api/company/${company_id}/analize-financial-data/`;
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

function onTabClick(e){
    const $clickedTab = $(e.target); 
    activeTab = $clickedTab.index(); 

    $clickedTab.siblings().removeClass("active-tab");
    $clickedTab.addClass("active-tab");

    $(".tab-body").empty().addClass("hidden").eq(activeTab).removeClass("hidden");
    drawTabBodies();
}

function initDashboard(){
    const $finDashboard = $('#fin-dashboard');
    $finDashboard.empty();

    const tabsContainer = $('<div>', {id: "tabs-container", class: "tabs-bar"})
    const tabBodiesContainer = $('<div>', {id: "tabbodies-container", class: "tabs-container"})

    $finDashboard.append(tabsContainer)
    $finDashboard.append(tabBodiesContainer)

    TAB_NAMES.forEach((name, index) => {
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
}

function drawDashboard(){
    if (!reportData) {
        return;
    }
    initDashboard();
    drawTabBodies();
}

function drawTabBodies(){
    if (!reportData) {
        return;
    }

    const tabBodiesContainer = $('#tabbodies-container');
    const currentTabBody = tabBodiesContainer.children().eq(activeTab)

    console.log();
    if (activeTab == 0) {
        drawTabFilters(currentTabBody);
    } else if (activeTab == 1) {
        drawTabDCF(currentTabBody);
    } else if (activeTab == 2) {
        drawTabData(currentTabBody);
    }

}

function showIndicatorChart(indicator, financialData) {
    const years = financialData.year;
    const values = financialData[indicator].map(v => v !== null ? v : null); 

    if (!years || !values || years.length !== values.length) {
        console.warn(`⚠️ No data available to draw the chart for ${indicator}`);
        return;
    }

    const data = [{
        x: years,
        y: values,
        name: indicator
    }];

    $('#chart-modal-content').empty();

    showModal(null, '<div id="chart-modal-content"></div>');

    setTimeout(() => {
        plotLineChart("chart-modal-content", data, `${indicator}`, "Year", indicator);
    }, 300); 

    $('#universal-modal').on('hidden.bs.modal', function () {
        $('#chart-modal-content').empty();
    });
}

function drawTabFilters(parent){
    function createFinancialFilterCard(filter) {
        const conditionClass = filter.condition ? "text-success" : "text-danger";
        const functionFormatted = filter.function.replace("_", " ").toUpperCase();
    
        const $card = $('<div>', { class: "card shadow-sm" });
    
        const $cardBody = $('<div>', { class: "card-body" });
    
        const $header = $('<div>', { class: "d-flex justify-content-between align-items-center" });
    
        const $title = $('<h5>', { 
            class: "card-title fw-bold text-primary mb-0", 
            text: `${filter.data} (${functionFormatted} over ${filter.periods} periods)`
        });
        const $weight = $('<span>', { class: "text-muted small",  text: `(Weight: ${filter.weight})` });
    
        $header.append($title, $weight);
    
        const $conditionText = $('<p>', { class: "mb-1 text-muted" });
        if (filter.check_type === "range") {
            $conditionText.text(`Value must be between ${filter.value1} and ${filter.value2}`);
        } else if (filter.check_type === "beyond") {
            $conditionText.text(`Value must be outside the range ${filter.value1} - ${filter.value2}`);
        } else if (filter.check_type === "above") {
            $conditionText.text(`Value must be above ${filter.value1}`);
        } else if (filter.check_type === "below") {
            $conditionText.text(`Value must be below ${filter.value1}`);
        }
    
        const $resultText = $('<p>', { 
            class: `fw-bold fs-5 ${conditionClass}`, 
            text: `Value: ${filter.result.toFixed(2)}` 
        });
    
        $cardBody.append($header, $conditionText, $resultText);
        $card.append($cardBody);
        return $card;
    }

    const scoreThreshold = 50
    const $tabContainer = $('<div>', { class: "filter-container" });
    $(parent).append($tabContainer);

    const financialData = reportData.financial_data;
    const financial_filters = reportData.financial_filters
    const filters = financial_filters.filters
    const sortedFilters = filters.sort((a, b) => {
        if (b.weight !== a.weight) {
            return b.weight - a.weight; 
        }
        return a.data.localeCompare(b.data); 
    });
    const finalScore = (100 * financial_filters.scores/financial_filters.total_scores).toFixed(2)

    const scoreClass = finalScore >= scoreThreshold ? "text-success" : "text-danger";

    const $headerCard = $('<div>', { class: "card shadow-sm" });
    const $headerBody = $('<div>', { class: "card-body" });

    const $headerTitle = $('<div>', { class: "d-flex justify-content-between align-items-center" });
    $headerTitle.append(
        $('<h4>', { class: "fw-bold mb-0", text: "Filters Pass Rate" }),
        $('<span>', { class: `fw-bold fs-5 ${scoreClass}`, text: `${finalScore} %` })
    );

    const $progressBar = $(`
        <div class="progress mt-2" style="height: 15px;">
            <div class="progress-bar ${scoreClass}" role="progressbar" style="width: ${finalScore}%;" aria-valuenow="${finalScore}" aria-valuemin="0" aria-valuemax="100"></div>
        </div>
    `);
    
    $headerBody.append($headerTitle, $progressBar);
    $headerCard.append($headerBody);
    $tabContainer.append($headerCard);

    if (sortedFilters){
        filters.forEach(filter => {
            const $filterCard = createFinancialFilterCard(filter);
            $filterCard.css("cursor", "pointer");
            $filterCard.on("click", function() {
                showIndicatorChart(filter.data, financialData)
            });
            $($tabContainer).append($filterCard)
        });
    }
}


function drawTabDCF(parent) {
    function renderDCFResults() {
        const $resultContainer = $("#dcf-result");
        $resultContainer.empty(); 
        
        if (dcf_valuations.length >0) {
            const avgFairPrice = (dcf_valuations.reduce((sum, r) => sum + r.fair_price, 0) / dcf_valuations.length).toFixed(2);
            const avgBuyPrice = (dcf_valuations.reduce((sum, r) => sum + r.buy_price, 0) / dcf_valuations.length).toFixed(2);
        
            const summaryCard = $(`
                <div class="card shadow-sm mt-3 shadow-sm bg-light">
                    <div class="card-body">
                        <h5 class="fw-bold text-dark">Avg Fair Value per Share: $${avgFairPrice}</h5>
                        <h5 class="text-danger">Avg Buy Price (with Margin of Safety): $${avgBuyPrice}</h5>
                        <p class="text-muted small">This is the average of all calculated DCF models.</p>
                    </div>
                </div>
            `);        
            $resultContainer.append(summaryCard);
        }

        dcf_valuations.forEach((result) => {
            const resultCard = $(`
                <div class="card shadow-sm mt-3 shadow-sm">
                    <div class="card-body">
                        <h5 class="fw-bold text-primary">${result.name}</h5>
                        <h6 class="fw-bold">Fair Value per Share: ${result.fair_price.toFixed(2)}</h6>
                        <h6 class="text-danger">Buy Price (with Margin of Safety): ${result.buy_price.toFixed(2)}</h6>
                        <p class="text-muted small">
                            Discount Rate: ${result.discount_rate}% | Terminal Growth Rate: ${result.terminal_growth_rate}% | Margin of Safety: ${result.margin_of_safety}% | Forecasted Years: ${result.years ?? "N/A"}
                        </p>
                    </div>
                </div>
            `);
            $resultContainer.append(resultCard);
        });

        if (dcf_valuations.length > 0) {
            drawFCFChart();
        }
    }

    function drawFCFChart() {
        const $chartContainer = $('<div>', { class: "card mt-3 shadow-sm" });
        const $chartBody = $('<div>', { class: "card-body" });
        const $chartDiv = $('<div>', { id: "fcf-chart", style: "width: 100%; height: 400px;" });
    
        $chartBody.append($chartDiv);
        $chartContainer.append($chartBody);
        $("#dcf-result").append($chartContainer);
    
        const financialData = reportData.financial_data;
        const historicalYears = financialData.year;
        const historicalFCF = financialData.FCF;
    
        const historicalTrace = {
            x: historicalYears,
            y: historicalFCF,
            mode: 'lines+markers',
            name: 'Historical FCF',
            line: { color: 'black', width: 2 }
        };
    
        const futureTraces = dcf_valuations.map((valuation, index) => {
            const futureYears = Array.from({ length: valuation.future_fcf.length }, (_, i) => historicalYears[historicalYears.length - 1] + i + 1);
            
            return {
                x: futureYears,
                y: valuation.future_fcf,
                mode: 'lines+markers',
                name: `${valuation.name}`,
                line: { width: 2 }
            };
        });
    
        plotLineChart("fcf-chart", [historicalTrace, ...futureTraces], "Historical and Projected FCF", "Years", "Free Cash Flow (FCF)");
    }
    
    const $tabContainer = $('<div>', { class: "filter-container" });
    $(parent).append($tabContainer);

    let lastShares = "";
    if (reportData) {
        const shares = reportData.financial_data.shares;
        lastShares = shares.length ? shares[shares.length - 1] : ""; 
    } 

    const $title = $('<h4>', { class: "fw-bold text-primary mb-3", text: "Discounted Cash Flow (DCF) Valuation" });

    const $form = $('<form>', { id: "dcf-form", class: "mb-3" });

    const fields = [
        { id: "shares", label: "Number of Shares", type: "number", value: lastShares, min: "1" },
        { id: "discount_rate", label: "Discount Rate (%)", type: "number", value: "15", min: "0", step: "0.1" },
        { id: "terminal_growth_rate", label: "Terminal Growth Rate (%)", type: "number", value: "2.5", min: "0", step: "0.1" },
        { id: "margin_of_safety", label: "Margin of Safety (%)", type: "number", value: "50", min: "0", step: "1" },
        { id: "years", label: "Years of Forecast", type: "number", value: "4", min: "1", step: "1" } 
    ];

    fields.forEach(field => {
        const $formGroup = $('<div>', { class: "mb-2" });
        const $label = $('<label>', { for: field.id, class: "form-label fw-bold", text: field.label });
        const $input = $('<input>', { 
            type: field.type, id: field.id, class: "form-control",
            value: field.value, min: field.min, step: field.step
        });
        $formGroup.append($label, $input);
        $form.append($formGroup);
    });

    const $fcfGroup = $('<div>', { class: "mb-2" });
    const $fcfLabel = $('<label>', { for: "future_fcf", class: "form-label fw-bold", text: "Future Cash Flows (comma-separated, optional)" });
    const $fcfInput = $('<input>', { type: "text", id: "future_fcf", class: "form-control", placeholder: "10000, 12000, 15000..." });
    $fcfGroup.append($fcfLabel, $fcfInput);
    $form.append($fcfGroup);

    const $submitBtn = $('<button>', { type: "button", class: "btn btn-primary w-100 mt-2", text: "Calculate" });
    $form.append($submitBtn);

    const $resultContainer = $('<div>', { id: "dcf-result", class: "mt-3" });

    $submitBtn.on("click", async function() {
        const requestData = {
            shares: parseInt($("#shares").val(), 10),
            discountRate: parseFloat($("#discount_rate").val()) / 100,
            terminalGrowthRate: parseFloat($("#terminal_growth_rate").val()) / 100,
            marginOfSafety: parseFloat($("#margin_of_safety").val()) / 100,
            years: parseInt($("#years").val(), 10),
            futureCashFlows: $("#future_fcf").val() ? $("#future_fcf").val().split(",").map(Number) : null
        };

        try {
            const url = `/api/company/${company_id}/dcf-valuation/`;
            const response = await fetch(url, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                 },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            dcf_valuations = data.valuations; 

            console.log(dcf_valuations)

            renderDCFResults(); 
        } catch (error) {
            console.error("Error fetching DCF valuation:", error);
            $resultContainer.html('<p class="text-danger">Error calculating DCF valuation.</p>');
        }
    });

    $tabContainer.append($title, $form, $resultContainer);

    renderDCFResults(); 
}


function drawTabData(parent) {
    const financialData = reportData.financial_data;
    const years = financialData.year;
    const indicators = Object.keys(financialData).filter(key => key !== "year" && key !== "id");

    const $tableContainer = $('<div>', { class: "fin-table-wrapper" }); 
    const $table = $('<table>', { class: "fin-table table table-sm table-bordered text-center" });

    const $thead = $('<thead>');
    const $headerRow = $('<tr>');
    $headerRow.append('<th class="text-start">Metric</th>');
    years.forEach(year => $headerRow.append(`<th>${year}</th>`));
    $thead.append($headerRow);
    $table.append($thead);

    const $tbody = $('<tbody>');
    indicators.forEach(indicator => {
        const $row = $('<tr>');
        const $indicatorCell = $('<td>', { class: "text-start text-primary clickable", text: indicator });

        $indicatorCell.on('click', () => showIndicatorChart(indicator, financialData));

        $row.append($indicatorCell);
        financialData[indicator].forEach(value => {
            let formattedValue = value !== null ? value.toLocaleString() : '-';
            if (indicator === "price" && value !== null) {
                formattedValue = parseFloat(value).toFixed(2);
            }
            $row.append(`<td>${formattedValue}</td>`);
        });

        $tbody.append($row);
    });

    $table.append($tbody);
    $tableContainer.append($table);
    $(parent).append($tableContainer);
}




