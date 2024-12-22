
export function loadImports() {
    let modulesSet = new Set();

    document.querySelectorAll('Import').forEach(module => {
        const modulesList = module.getAttribute('data-modules');

        if (modulesList) {
            modulesList.split(' ').forEach(mod => {
                modulesSet.add(mod);
            });
        }
    });

    const promises = Array.from(modulesSet).map(mod => loadImport(mod));
    return Promise.all(promises).then(() => Array.from(modulesSet));
}

function loadImport(mod) {
    switch (mod) {
        case 'd3':
            return import(/* webpackChunkName: "d3" */ 'd3').then(module => { window.app["d3"] = module; });
        case 'pandas':
            return import(/* webpackChunkName: "pd" */ 'pandas-js').then(module => { window.app["pd"] = module; });
        case 'findashboard':
            return Promise.all([
                import(/* webpackChunkName: "findashboard" */ './css/findashboard.css').then(() => {
                    console.log("CSS for Findashboard loaded");
                }),
                import(/* webpackChunkName: "fd" */ './js/findashboard').then(module => { 
                    console.log("JS for Findashboard loaded");
                    window.app["fd"] = module; 
                }),
            ]);
        case 'processcsvdata':
            return Promise.all([
                import(/* webpackChunkName: "processcsvdata" */ './css/processcsvdata.css').then(() => {
                    console.log("CSS for processcsvdata loaded");
                }),
                import(/* webpackChunkName: "processcsvdata" */ './js/processcsvdata').then(module => {
                    console.log("JS for processcsvdata loaded");
                 }),
            ]);
        default:
            console.warn(`No module found for ${mod}`);
            return Promise.resolve();
    }

}
