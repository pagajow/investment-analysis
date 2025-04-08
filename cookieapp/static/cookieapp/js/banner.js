document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("cookie-form");

    form.addEventListener("submit", function (e) {
        e.preventDefault(); 

        const selected = [];
        const checkboxes = form.querySelectorAll("input[name='cookies']:checked");
        const formData = new URLSearchParams();
        checkboxes.forEach(cb => {
            formData.append("cookies", cb.value);
        });


        fetch("/cookie/set/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": window.csrfToken,
            },
            body: formData,
        }).then(() => {
            document.getElementById("cookie-banner").style.display = "none";
        });
    });

    document.getElementById("btn-accept-all").addEventListener("click", function () {
        fetch("/cookie/accept-all/", {
            method: "POST",
            headers: {
                "X-CSRFToken": window.csrfToken,
            },
        }).then(() => {
            document.getElementById("cookie-banner").style.display = "none";
        });
    });

    document.getElementById("btn-accept-essentials").addEventListener("click", function () {
        fetch("/cookie/decline-all/", {
            method: "POST",
            headers: {
                "X-CSRFToken": window.csrfToken,
            },
        }).then(() => {
            document.getElementById("cookie-banner").style.display = "none";
        });
    });
});


