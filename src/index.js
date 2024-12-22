import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';
import $ from 'jquery';
import './css/base.css';


window.app = window.app || {};
window.app["$"] = $;

// Dinamic import based on custom html tag <Import data-modeles="module1 module2 ..."> and atribute "data-modules"
import { loadImports } from "./imports.js";
document.addEventListener("DOMContentLoaded", () => {
    manageSidebar();

    loadImports().then((modules) => {
        const e = new CustomEvent("ImportCompleted",  { detail: { modules } });
        window.dispatchEvent(e);
    });
});


function manageSidebar() {
    console.log("MANAGE SIDE BAR")
    const sidebar = document.querySelector('.sidebar-wrapper');
    const toggleButton = document.getElementById('toggle-sidebar');

    const isSidebarHidden = localStorage.getItem('sidebarHidden') === 'true';
    if (isSidebarHidden) {
        sidebar.classList.add('hidden');
    }

    toggleButton.addEventListener('click', () => {
        sidebar.classList.toggle('hidden');
        const isHidden = sidebar.classList.contains('hidden');
        localStorage.setItem('sidebarHidden', isHidden);
    });
}