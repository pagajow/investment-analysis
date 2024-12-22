import * as d3 from 'd3';
import $ from 'jquery';
export const drawChart = ($container, data, xName, yNames, horizontalLines = []) => {
    const chartId = $container.attr('id');

    // Pobieramy dane x oraz y dla każdej serii
    const xData = data[xName];

    // Oblicz dostępne miejsce
    const containerWidth = $container.width(); // używamy jQuery do uzyskania szerokości
    const containerHeight = $container.height(); // używamy jQuery do uzyskania wysokości

    // Ustawienia wykresu
    const margin = { top: 20, right: 20, bottom: 50, left: 100 };
    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;

    // Skala osi X
    const x = d3.scaleBand()
        .domain(xData)
        .range([0, width])
        .padding(0.1);

    // Skala osi Y
    const minY = d3.min(yNames.flatMap(name => data[name]).filter(d => d !== null)); // Ignorowanie null
    const maxY = d3.max(yNames.flatMap(name => data[name]).filter(d => d !== null)); // Ignorowanie null
    const y = d3.scaleLinear()
        .domain([minY, maxY])
        .nice()
        .range([height, 0]);

    // Tworzenie SVG (czyści wcześniej istniejące wykresy)
    d3.select(`#${chartId} svg`).remove();
    const svg = d3.select(`#${chartId}`).append("svg")
        .attr("width", containerWidth)
        .attr("height", containerHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Tworzenie osi X z etykietami lat
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).tickFormat(d3.format("d")));

    // Tworzenie osi Y
    svg.append("g")
        .call(d3.axisLeft(y).ticks(10).tickFormat(d => d.toLocaleString("en-US")))
        .selectAll("text")
        .attr("dx", "-0.5em");

    // Kolory dla różnych linii
    const colors = d3.scaleOrdinal(d3.schemeCategory10);

    // Rysowanie linii dla każdej z nazw y
    yNames.forEach((yName, index) => {
        const lineData = data[yName];

        // Sprawdzamy, czy dane są prawidłowe przed rysowaniem linii
        if (!lineData || lineData.every(d => d === null)) {
            console.warn(`No data for ${yName}, skipping chart`);
            return; // Jeśli wszystkie dane są null, nie rysujemy wykresu
        }

        // Filtrujemy dane, aby pominąć null
        const filteredData = lineData.map((value, idx) => (value === null ? undefined : value));

        // Rysowanie linii tylko dla dostępnych danych
        const line = d3.line()
            .x((d, i) => x(xData[i]) + x.bandwidth() / 2) // Przesunięcie do środka słupka
            .y(d => (d === undefined ? y(0) : y(d))) // Jeśli wartość jest undefined, nie rysuj linii (pomiń ją)

        svg.append("path")
            .data([filteredData])
            .attr("class", "line")
            .attr("d", line)
            .attr("fill", "none")
            .attr("stroke", colors(index))
            .attr("stroke-width", 2);
    });

    // Dodanie poziomej linii
    horizontalLines.forEach((line) => {
        svg.append("line")
            .attr("x1", 0)
            .attr("y1", y(line.value))
            .attr("x2", width)
            .attr("y2", y(line.value))
            .attr("stroke", line.color || "black")
            .attr("stroke-width", 2)
            .attr("stroke-dasharray", "5,5");

        // Dodanie etykiety dla poziomej linii
        svg.append("text")
            .attr("x", width - 10)
            .attr("y", y(line.value) - 10)
            .style("text-anchor", "end")
            .style("fill", line.color || "black")
            .text(line.label || `Line at ${line.value}`);
    });

    // Dodanie etykiety osi Y
    svg.append("text")
        .attr("y", 0 - margin.left + 10)
        .attr("x", 0 - margin.top)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text('Revenue');

    // Dodanie legendy na dole
    const legend = svg.append("g")
        .attr("transform", `translate(0, ${height + 20})`);

    // Dodanie elementów legendy
    yNames.forEach((yName, index) => {
        legend.append("circle")
            .attr("cx", (index * 150) + 20)  // Przesunięcie w poziomie
            .attr("cy", 10)
            .attr("r", 6)
            .style("fill", colors(index));

        legend.append("text")
            .attr("x", (index * 150) + 40)  // Przesunięcie w poziomie
            .attr("y", 10)
            .attr("dy", ".35em")  // Wyśrodkowanie w pionie
            .style("text-anchor", "start")
            .style("font-size", "12px")
            .text(yName.replace(/_/g, " "));
    });

    return chartId;
};

export function addSummmaryCard(parent, cardId, big5, health, dcf) {
    const $container = $('<div>', {
        id: cardId,
        class: "fin-element"
    });

    $(parent).append($container);

    const price = dcf.price ? dcf.price.toFixed(2) : "---"
    const currency = dcf.price && dcf.currency ? dcf.currency : ""
    const price_date = dcf.price  && dcf.currency && ` (at ${dcf.price_updated})` ? dcf.price_updated : ""

    $container.append($('<h6>').text(`DCF Valuation: ${dcf.value.toFixed(2)} ${currency} | Price: ${price} ${currency} ${price_date}`));
 
    const pointsBig5 = Object.values(big5).filter(v => v.met > 0).length;
    const totalPointsBig5 = Object.keys(big5).length;
    const $big5Section = $('<div>').append($('<h6>').text(`Big 5 Metrics (${pointsBig5}/${totalPointsBig5}):`));
    $big5Section.addClass("fin-summary-section")
    const $big5List = $($big5Section).append("<ul>")
    Object.entries(big5).forEach(([key, metric]) => {
        $big5List.append(
            $("<li>").text(`${key.replace(/_/g, " ").toUpperCase()}: ${metric.value.toFixed(2)} (${metric.met ? "+" : "-"})`)
        );
    });
    $container.append($big5Section);

    const pointsHealth = Object.values(health).filter(v => v.met > 0).length;
    const totalPointsHealth = Object.keys(health).length;
    const $healthSection = $('<div>').append($('<h6>').text(`Health Metrics (${pointsHealth}/${totalPointsHealth}):`));
    $healthSection.addClass("fin-summary-section")
    const $healthList = $($healthSection).append("<ul>")
    Object.entries(health).forEach(([key, metric]) => {
        $healthList.append(
            $("<li>").text(`${key.replace(/_/g, " ").toUpperCase()}: ${metric.value.toFixed(2)} (${metric.met ? "+" : "-"})`)
        );
    });
    $container.append($healthSection);
}
