/*
    // Color CONSTs
const DK_BG =        '#282828';
const DK_RED =       '#cc241d';
const DK_GREEN =     '#98971a';
const DK_YELLOW =    '#d79921';
const DK_BLUE =      '#458588';
const DK_PURPLE =    '#b16286';
const DK_AQUA =      '#689d6a';
const DK_GRAY =      '#928374';
const DK_ORANGE =    '#d65d0e';

const LG_BG =        '#ebdbb22'
const LG_RED =       '#fb4934';
const LG_GREEN =     '#b8bb26';
const LG_YELLOW =    '#fabd2f';
const LG_BLUE =      '#83a598';
const LG_PURPLE =    '#d3869b';
const LG_AQUA =      '#8ec07c';
const LG_GRAY =      '#a89984';
const LG_ORANGE =    '#fe8019';
*/

// Misc functions
function id(node) {
    return `${node.parent ? id(node.parent) + "." : ""}${node.data.name}`;
}

function bilink(root) {
    const map = new Map(root.leaves().map(d => [id(d), d]));
    for (const d of root.leaves()) d.incoming = [], d.outgoing = d.data.imports.map(i => [d, map.get(i)]);
    for (const d of root.leaves()) for (const o of d.outgoing) o[1].incoming.push(o);
    return root;
}

function hierarchy(data, delimiter = ".") {
    let root;
    const map = new Map;
    data.forEach(function find(data) {
        const {name} = data;
        if (map.has(name)) return map.get(name);
        const i = name.lastIndexOf(delimiter);
        map.set(name, data);
        if (i >= 0) {
            find({name: name.substring(0, i), children: []}).children.push(data);
            data.name = name.substring(i + 1);
        } else {
            root = data;
        }
        return data;
    });
    return root;
}



function draw_eb(data) {
    const colorin = LG_GREEN;
    const colorout = LG_YELLOW;
    const colornone = LG_GRAY;

    const width = 700;
    const margint_top = 100;
    const margint_right = 10;
    const margint_bottom = 100;
    const margint_left = 100;

    const radius = width / 2;

    const tree = d3.cluster()
        .size([2 * Math.PI, radius - 100])

    const root = tree(bilink(d3.hierarchy(data)
        .sort((a, b) => d3.ascending(a.height, b.height) || d3.ascending(a.data.name, b.data.name))));

    const svg = d3.select("svg#svg_eb")
        .attr("width", width)
        .attr("height", width)
        .attr("viewBox", [-width / 2, -width / 2, width, width])
        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

    d3.select("div#container_eb")
        .attr("style",  "width: 100%;" +
            `border: 1px solid ${LG_GRAY};` +
            "padding: 10px;" + 
            "border-radius: 5px;" + 
            "margin-top: 10px;" 
        );

    const node = svg.append("g")
        .selectAll()
        .data(root.leaves())
        .join("g")
        .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`)
        .append("text")
        .attr("class", "eb_leave")
        .attr("font-weight", 300)
        .attr("style", "font-family: 'Courier New', monospace;")
        .attr("fill", LG_GRAY)
        .attr("dy", "0.31em")
        .attr("x", d => d.x < Math.PI ? 6 : -6)
        .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
        .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
        .text(d => d.data.name)
        .attr("style", "font-family: 'Courier New', monospace;")
        .each(function(d) { d.text = this; })
        .on("mouseover", overed)
        .on("mouseout", outed)
        .call(text => {
            text.append("title").text(d => `${d.data.name}
                ${d.outgoing.length} outgoing
                ${d.incoming.length} incoming`)
        });

    const line = d3.lineRadial()
        .curve(d3.curveBundle.beta(0.85))
        .radius(d => d.y)
        .angle(d => d.x);

    const BLEND_IN = "normal";
    const BLEND_OUT = "normal";

    const link = svg.append("g")
        .attr("stroke", DK_GRAY)
        .attr("fill", "none")
        .selectAll()
        .data(root.leaves().flatMap(leaf => leaf.outgoing))
        .join("path")
        .style("mix-blend-mode", BLEND_OUT)
        .style("opacity", 0.2)
        .attr("d", ([i, o]) => line(i.path(o)))
        .each(function(d) { d.path = this; });

    function overed(event, d) {
        // when the mouse is over
        d3.select(this)
            .attr("style", "text-decoration: none;")
            .attr("fill", "white")
            .attr("font-weight", "bold");

        link.style("mix-blend-mode", BLEND_IN);
        link.attr("stroke", LG_GRAY);

        d3.selectAll(d.incoming.map(d => d.path))
            .attr("stroke", colorin).raise();

        d3.selectAll(d.incoming.map(([d]) => d.text))
            .attr("fill", colorin)
            .attr("font-weight", 900);

        d3.selectAll(d.outgoing.map(d => d.path))
            .style("opacity", 1)
            .attr("stroke", colorout).raise();

        d3.selectAll(d.outgoing.map(([, d]) => d.text))
            .attr("fill", colorout)
            .attr("font-weight", 900);
    }

    function outed(event, d) {
        // when the mouse leaves the object
        link.style("mix-blend-mode", BLEND_OUT);
        link.attr("stroke", DK_GRAY)
        d3.select(this)
            .attr("style", "text-decoration: none;")
            .attr("fill", DK_GRAY)
            .attr("font-weight", "normal");

        d3.select(this)
            .attr("font-weight", null);

        d3.selectAll(d.incoming.map(d => d.path))
            .attr("stroke", null);

        d3.selectAll(d.incoming.map(([d]) => d.text))
            .attr("fill", LG_GRAY)
            .attr("font-weight", 300);

        d3.selectAll(d.outgoing.map(d => d.path))
            .attr("stroke", null);

        d3.selectAll(d.outgoing.map(([, d]) => d.text))
            .attr("fill", LG_GRAY)
            .attr("font-weight", 300);
    }

}


fetch('../data/flare.json')
    .then(res => res.json())
    .then(data => hierarchy(data))
    .then(data => draw_eb(data));
