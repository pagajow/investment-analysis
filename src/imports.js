
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
                import(/* webpackChunkName: "findashboard" */ './css/analysisapp/findashboard.css').then(() => {
                    console.log("CSS for Findashboard loaded");
                }),
                import(/* webpackChunkName: "fd" */ './js/analysisapp/findashboard').then(module => { 
                    window.app["fd"] = module; 
                }),
            ]);
        case 'processcsvdata':
            return Promise.all([
                import(/* webpackChunkName: "processcsvdata" */ './css/analysisapp/processcsvdata.css').then(() => {}),
                import(/* webpackChunkName: "processcsvdata" */ './js/analysisapp/processcsvdata').then(module => {}),
            ]);
        case 'askai':
            return Promise.all([
                //import(/* webpackChunkName: "askai" */ './css/askai.css').then(() => {}),
                import(/* webpackChunkName: "askai" */ './js/agentapp/askai').then(module => {}),
            ]);
        case 'airesearch':
            return Promise.all([
                import(/* webpackChunkName: "airesearch" */ './js/agentapp/airesearch').then(module => {}),
            ]);
        default:
            console.warn(`No module found for ${mod}`);
            return Promise.resolve();
    }

}
