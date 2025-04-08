import $ from 'jquery';

const maxCharCount = 2000;

window.addEventListener("ImportCompleted", event => {
    const $companySelect = $("#company-select");
    const $fileUpload = $("#file-upload");
    const $fileList = $("#file-list");
    const $queryText = $("#query-text");
    const $charCount = $("#char-count");
    const $submitButton = $("#submit-research");
    const $statusMessages = $("#status-messages");

    let selectedFiles = [];

    $queryText.on("input", function() {
        const remaining = maxCharCount - $(this).val().length;
        $charCount.text(remaining);
    });

    $fileUpload.on("change", function () {
        $fileList.empty();
        selectedFiles = Array.from(this.files).slice(0, 10);
        selectedFiles.forEach(file => {
            $fileList.append(`<li>${file.name} (${(file.size / 1024).toFixed(2)} KB)</li>`);
        });
    });

    
    $submitButton.on("click", function () {
        const selectedCompany = $companySelect.val();
        const query = $queryText.val();

        if (!selectedCompany) {
            clearStatus();
            showError("Please Select an asset.");
            return;
        }

        clearStatus();
        showLoading(selectedCompany);

        const formData = new FormData();
        formData.append("company_id", selectedCompany);
        formData.append("query", query);
        selectedFiles.forEach((file) => {
            formData.append("file", file);
        });

        fetch("/ai/ai-research/", {
            method: "POST",
            headers: { "X-CSRFToken": window.csrfToken },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            clearStatus();
            if (data.redirect) {
                showSuccess("Report generated successfully", data.redirect);
            } else if (data.error) {
                showError(data.error);
            }
        })
        .catch(error => {
            clearStatus();
            showError("Error: " + error.message);
        });

        $queryText.val("");
        $charCount.text(maxCharCount);
        $companySelect.val("");
        $fileUpload.val("");
        $fileList.empty();
    });

    function clearStatus() {
        $statusMessages.empty();
    }

    function showLoading(company_id) {
        const url = `/company/${company_id}/finreports/`;
        $statusMessages.html(`
            <div>
                <div class="spinner"></div>
                <p class="mt-3">Your report will show up <a href="${url}" class="">here</a> when its finished.</p>
            </div>
        `);
    }

    function showSuccess(message, redirectUrl) {
        $statusMessages.html(`
            <div class="status success">
                <p>${message}</p>
                <a href="${redirectUrl}" class="btn-report">to report</a>
            </div>
        `);
    }

    function showError(message) {
        $statusMessages.html(`
            <div class="status error">
                <span>${message}</span>
            </div>
        `);
    }
});
