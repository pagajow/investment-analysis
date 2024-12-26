import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';
import $ from 'jquery';
import './css/base.css';
import './css/tables.css';


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
    const $sidebar = $('.sidebar-wrapper'); 
    const $toggleButton = $('#toggle-sidebar'); 
    const $icon = $toggleButton.find('i'); 

    const isSidebarHidden = localStorage.getItem('sidebar-hidden') === 'true';
    if (isSidebarHidden) {
        $sidebar.addClass('sidebar-hidden');
        $icon.removeClass('fa-arrow-left').addClass('fa-arrow-right');
    }

    $toggleButton.on('click', () => {
        $sidebar.toggleClass('sidebar-hidden'); // Ukryj/pokaż pasek boczny
        const isHidden = $sidebar.hasClass('sidebar-hidden');
        if (isHidden) {
            $icon.removeClass('fa-arrow-left').addClass('fa-arrow-right');
        } else {
            $icon.removeClass('fa-arrow-right').addClass('fa-arrow-left');
        }
        localStorage.setItem('sidebar-hidden', isHidden);
    });
}