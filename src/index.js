import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';
import './css/base.css';
import './css/tables.css';
import { showModal } from './utils';


window.app = window.app || {};
window.app["$"] = $;
window.app["showModal"] = showModal;

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

    $toggleButton.on('click', () => {
        $sidebar.toggleClass('sidebar-hidden'); 
        const isHidden = $sidebar.hasClass('sidebar-hidden');
        if (isHidden) {
            $icon.removeClass('fa-bars').addClass('fa-bars');
        } else {
            $icon.removeClass('fa-bars').addClass('fa-bars');
        }
        document.cookie = `menu_fold=${isHidden ? 1 : 0}; path=/; max-age=31536000; SameSite=Lax; Secure;`;
    });
}
