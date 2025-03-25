import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.min.css';
import * as bootstrap from 'bootstrap';



export function getApiUrl(endpoint) {
    const baseUrl = window.serverBaseUrl || "http://localhost:8000";
    const url = `${baseUrl}/${endpoint}`;
    return url;
}

export function getCSRFToken() {
    return window.csrfToken;
}

export async function getData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        } else {
            const data = await response.json();
            return data;
        }
    } catch (error) {
        console.error('Error getData:', error);
        return null;
    }
}

export async function postData(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken 
            },
            body: JSON.stringify(data)
        })
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        } else {
            const data = await response.json();
            return data;
        }
    } catch (error) {
        console.error('Error postData:', error);
        return null;
    }
}


export function showModal(title, content, options = {}) {
    const modalHeader = $("#modal-header"); 
    const modalTitle = $("#modal-title");

    if (title === null || title === undefined) {
        modalTitle.text("");
    } 

    $("#modal-body").html(content);
    
    if (options.footer === false) {
        $("#modal-footer").hide();
    } else {
        $("#modal-footer").show();
    }

    if (options.size === "small") {
        $("#universal-modal .modal-dialog").removeClass("modal-lg").addClass("modal-sm");
    } else {
        $("#universal-modal .modal-dialog").removeClass("modal-sm").addClass("modal-lg");
    }

    const modalElement = document.getElementById('universal-modal');
    const bsModal = new bootstrap.Modal(modalElement);
    bsModal.show();
}
