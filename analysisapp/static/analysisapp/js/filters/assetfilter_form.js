document.addEventListener("DOMContentLoaded", function () {
    const checkTypeField = document.getElementById("id_check_type");
    const value1Field = document.getElementById("id_value1");
    const value2Field = document.getElementById("id_value2");
    const value2Container = value2Field.closest("p");
    
    function updateFormFields() {
        let checkType = checkTypeField.value;

        // Ukrywanie / Pokazywanie value2
        if (checkType === "above" || checkType === "below") {
            value2Container.style.display = "none";
            value2Field.value = value1Field.value;
        } else {
            value2Container.style.display = "block";
        }

        // Dynamiczna zmiana etykiet
        const value1Label = document.querySelector("label[for='id_value1']");
        const value2Label = document.querySelector("label[for='id_value2']");

        if (checkType === "above") {
            value1Label.textContent = "Threshold";
        } else if (checkType === "below") {
            value1Label.textContent = "Threshold";
        } else if (checkType === "range") {
            value1Label.textContent = "Lower Threshold";
            value2Label.textContent = "Upper Threshold";
        } else if (checkType === "beyond") {
            value1Label.textContent = "Lower Threshold";
            value2Label.textContent = "Upper Threshold";
        }
    }

    // Uruchomienie na starcie i na zmianę pola
    updateFormFields();
    checkTypeField.addEventListener("change", updateFormFields);
});
