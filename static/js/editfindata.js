function getApiUrl(endpoint) {
    const baseUrl = window.serverBaseUrl || "http://localhost:8000";
    const url = `${baseUrl}/${endpoint}`;
    return url;
}

function addRow(event, begin=true){
    const noDataTag = document.querySelector('#financial-data-table tbody tr td#no_financial_data');
    if (noDataTag !== null) {
        noDataTag.closest("tr").remove();
    }

    const tableBody = document.querySelector('#financial-data-table tbody');
    const newRow = document.createElement("tr");

    const cols = document.querySelectorAll('#financial-data-table thead th[data-field]');

    newRow.innerHTML += `<th class="short-column"><i class="fas fa-trash-alt text-secondary delete-row" style="cursor: pointer;"></i></th>`;
    cols.forEach(function(col) {
        const field = col.getAttribute('data-field');
        if (field === 'id') {
            cellContent = `<td class="short-column hidden" data-field="${field}" data-year="">-</td>`;
        } else if (field === 'year') {
            cellContent = `<td data-field="${field}" data-year=""><input class="short-column" type="number" min="0" step="1" name="${field}" value=""/></td>`;
        } else {
            cellContent = `<td data-field="${field}" data-year=""><input type="number" name="${field}" value="" /></td>`;
        }

        newRow.innerHTML += cellContent;
    });

    if (begin) {
        tableBody.prepend(newRow);
    } else {
        tableBody.appendChild(newRow);
    }

    const deleteButton = newRow.querySelector('.delete-row');
    deleteButton.addEventListener('click', deleteRow);
}

function addRowAtTheBegin(event) {
    addRow(event, true);
}
function addRowAtTheEnd(event) {
    addRow(event, false);
}
function deleteRow(event) {
    const row = event.target.closest('tr');  
    row.remove();  
}


function collectTableData() {
    const rows = document.querySelectorAll('#financial-data-table tbody tr');
    const companyId = document.getElementById('company-id').textContent;

    let dataToSend = [];
    let years = new Set();

    rows.forEach(function(row) {
        let rowData = {};
        let year = row.querySelector('input[name="year"]').value;

        if (!validateData(year, years)) {
            return;  
        }

        years.add(year);
        rowData["year"] = year;

        const idCell = row.querySelector('td[data-field="id"]');
        rowData["id"] = (idCell && idCell.textContent.trim() === "-") ? "new" : idCell.textContent.trim();

        const inputs = row.querySelectorAll('input');
        inputs.forEach(function(input) {
            const fieldName = input.getAttribute('name');
            const fieldValue = input.value;
            if (fieldValue === "") {
                rowData[fieldName] = null; 
            } else {
                rowData[fieldName] = parseFloat(fieldValue); 
            }
        });

        dataToSend.push(rowData);
    });


    const overwriteAll = document.getElementById("overwrite-all").checked;
    return {
        "company_id": companyId,
        "data": dataToSend,
        "overwrite_all": overwriteAll ? 1 : 0,
    };
}

function validateData(year, years) {
    if (!year || years.has(year)) {
        console.error(`Year ${year} must be unique and non-empty.`);
        return false;
    }
    return true;
}

function sendDataToServer(data) {
    const url = `api/company/${data.company_id}/override-financial-data/`;  

    fetch(getApiUrl(url), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken  
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = data.redirect_url;
        } else {
            console.error('Error - storing data:', data);
        }
    })
    .catch((error) => {
        console.error('ERROR:', error);
    });
}


function processTableDataAndSend() {
    const collectedData = collectTableData();
    sendDataToServer(collectedData);
}

function saveData() {
    const userConfirmed = confirm("Are you sure you want to override the date?");
        
    if (userConfirmed) {
        processTableDataAndSend();
    }
}

function sortTableData() {
    const tableBody = document.querySelector('#financial-data-table tbody');
    const rows = Array.from(tableBody.querySelectorAll('tr')); 

    rows.sort(function(rowA, rowB) {
        const yearA = rowA.querySelector('input[name="year"]').value;
        const yearB = rowB.querySelector('input[name="year"]').value;
        
        return parseInt(yearA) - parseInt(yearB);
    });

    while (tableBody.firstChild) {
        tableBody.removeChild(tableBody.firstChild);
    }

    rows.forEach(function(row) {
        tableBody.appendChild(row);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll('#financial-data-table input');
    inputs.forEach((input) => {
        input.addEventListener('input', function () {
            const fieldName = this.getAttribute('name'); 
            const newValue = this.value;  
        });
    });

    const addRowBtnEnd = document.getElementById("add-row-end-btn")
    const addRowBtnBegin = document.getElementById("add-row-begin-btn")
    addRowBtnEnd.addEventListener('click', addRowAtTheEnd);
    addRowBtnBegin.addEventListener('click', addRowAtTheBegin);

    const deleteButtons = document.querySelectorAll('.delete-row');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', deleteRow);
    });


    document.getElementById('save-data-btn').addEventListener('click', saveData);
})