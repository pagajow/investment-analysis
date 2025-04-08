import $ from 'jquery';


let fields = [];
let selectedFields = {}; 

window.addEventListener("ImportCompleted", event => {
    $("#field_list li").each((index, element) => fields.push($(element).data('field')));

    $(".field-selector").on("change", onSelectionChange);
    $("#save-data-btn").on("click", sendData);

    $("#btn-msnmoney").on("click", formatDataMSNMoney);

    $('[data-bs-toggle="tooltip"]').tooltip();
});

function formatDataMSNMoney(event) {
    $("#raw-data-table tbody input").each((index, ele) => {
        let value = $(ele).val().trim(); 
    
        if (value === "-") {
            $(ele).val("");
        } else if (/^-?\d+(\.\d+)?M$/.test(value)) {
            const num = parseFloat(value.slice(0, -1)); 
            $(ele).val(num * 1000000);
        } else if (/^-?\d+(\.\d+)?[KT]$/.test(value)) {
            const num = parseFloat(value.slice(0, -1)); 
            $(ele).val(num * 1000); 
        } else if (/^-?\d+(\.\d+)?B$/.test(value)) {
            const num = parseFloat(value.slice(0, -1)); 
            $(ele).val(num * 1000000000); 
        }
    });
}

function onSelectionChange(event) {
    const selectedField = $(this).val(); 
    const column = $(this).parent().data("column"); 

    this.setAttribute("title", selectedField || "None");

    if (selectedField) {
        $(".field-selector").not(this).find(`option[value='${selectedField}']`).prop("disabled", true);
        const previouslySelectedField = selectedFields[column];
        if (previouslySelectedField) {
            $(".field-selector").find(`option[value='${previouslySelectedField}']`).prop("disabled", false);
        }
        selectedFields[column] = selectedField;
    } else {
        const previouslySelectedField = selectedFields[column];
        if (previouslySelectedField) {
            $(".field-selector").find(`option[value='${previouslySelectedField}']`).prop("disabled", false);
        }
        delete selectedFields[column];
    }

    console.log("Selected fields:", selectedFields);
}

function sendData(event) {
    const data = {}; 
    
    const overwriteAll = document.getElementById("overwrite-all").checked;
    const dataToSend = { 
        "data": data, 
        "company_id": $("#raw-data-table").data("company-id"),
        "overwrite_all": overwriteAll ? 1 : 0,
    };
    const table = $(".table tbody"); 

    Object.values(selectedFields).forEach(field => {
        data[field] = []; 
    });

    table.find("tr").each(function() {
        const cells = $(this).find("input");

        Object.entries(selectedFields).forEach(([columnName, fieldName]) => {
            const columnIndex = $(`#raw-data-table thead th[data-column="${columnName}"]`).index();

            if (columnIndex !== -1) {
                const cellValue = $(cells[columnIndex]).val().trim();
                data[fieldName].push(cellValue);
            }
        });
    });

    console.log("Data to send:", dataToSend);

    if (!validateData(dataToSend.data)) {
        return
    }

    const userConfirmed = confirm("Are you sure you want to override the date?");
    if (userConfirmed) {
        dataToSend.data = transformData(dataToSend.data)
        sendDataToServer(dataToSend)
    }
}

function transformData(obj) {
    const keys = Object.keys(obj); 
    const length = obj[keys[0]].length; 
    const result = []; 

    for (let i = 0; i < length; i++) {
        const row = {}; 
        keys.forEach(key => {
            row[key] = parseInt(obj[key][i]); 
        });
        result.push(row);
    }
    return result;
}

function sendDataToServer(data) {
    const url = `/api/company/${data.company_id}/override-financial-data/`;  

    fetch(url, {
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
            console.log('Data saved successfully.');
            window.location.href = data.redirect_url;
        } else {
            console.error('Error while saving data:', data);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function validateData(data) {
    const necessaryKeys = ["year"];

    if (necessaryKeys.some(key => !(key in data))) {
        alert(`You need to include clumns: ${necessaryKeys}`)
        return false;
    }

    if (!(data.year.every(item => Number.isInteger(Number(item.trim()))))) {
        alert(`Column "year" has to contain only integers!`)
        return false;
    }

    return true;
}