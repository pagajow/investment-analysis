export function getApiUrl(endpoint) {
    const baseUrl = window.serverBaseUrl || "http://localhost:8000";
    const url = `${baseUrl}/${endpoint}`;
    return url;
}

export function getCSRFToken() {
    return window.csrfToken;
}