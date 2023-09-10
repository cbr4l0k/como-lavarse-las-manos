// es.colorlitelens.com/images/tesztek/huetest/Farnsworth100.html 

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

const COLOR = (d) => d._children ? LG_GREEN : LG_YELLOW;

function draw_tree(data) {

    data.children = data.children.filter((c)=> c.type != 'External dependency');


    const width = 928;
    const marginTop = 100;
    const marginRight = 10;
    const marginBottom = 100;
    const marginLeft = 100;

    const root = d3.hierarchy(data);
    const dx = 35;
    const dy = (width - marginRight - marginLeft) / (1 + root.height);

    const tree = d3.tree().nodeSize([dx, dy]);
    const diagonal = d3.linkHorizontal().x(d => d.y).y(d => d.x);

    const env = d3.select("div.container_general#tree");

    env.select("div#container_tree")
        .attr("style",  "width: 90%;" +
                        `border: 1px solid ${LG_GRAY};` +
                        "border-radius: 5px;" + 
                        "margin-top: 10px;"  +
                        "overflow-x: scroll;" +
                        "overflow-y: scroll;"
        );

    const svg = d3.select("svg#svg_tree")
        .attr("viewBox", [-marginLeft, -marginTop, width, dx])
        .attr("style",  "max-width: 100%;" + 
                        "overflow-y: scroll;" +
                        "height: auto; " +
                        "font: 10px sans-serif; " + 
                        "user-select: none; " +
                        `background-color: ${DK_BG}`);


    const gLink = svg.append("g")
        .attr("fill", "none")
        .attr("stroke", LG_GRAY)
        .attr("stroke-opacity", 0.5)
        .attr("stroke-width", 1.5);

    const gNode = svg.append("g")
        .attr("cursor", "pointer")
        .attr("pointer-events", "all");

    function update(event, source) {
        const duration = event?.altKey ? 2500 : 250;
        const nodes = root.descendants().reverse();
        const links = root.links();

        tree(root);

        let left = root;
        let right = root;
        root.eachBefore(node => {
            if (node.x < left.x) left = node;
            if (node.x > right.x) right = node;
        });

        const height = right.x - left.x + marginTop + marginBottom;

        const transition = svg.transition()
            .duration(duration)
            .attr("height", height)
            .attr("viewBox", [-marginLeft, left.x - marginTop, width, height])
            .tween("resize", window.ResizeObserver ? null : () => () => svg.dispatch("toggle"));

        const node = gNode.selectAll("g")
            .data(nodes, d => d.id);


        const nodeEnter = node.enter().append("g")
            .attr("transform", d => `translate(${source.y0},${source.x0})`)
            .attr("fill-opacity", 0)
            .attr("stroke-opacity", 0)
            .on("click", (event, d) => {
                d.children = d.children ? null : d._children;
                update(event, d);
            })
            .on("mouseover", (event, d) => {
                d3.select("code#desc_tree").html(`<b style='text-decoration: underline; color: ${COLOR(d)}'>${d.data.name}</b><br><br> ${d.data.explanation}`)
            });

        nodeEnter.append("circle")
            .attr("r", 2.5)
            .attr("fill", d => d._children ? DK_GREEN : LG_YELLOW)
            .attr("stroke-width", 10);

        nodeEnter.append("text")
            .attr("dy", "0.31em")
            .attr("x", d => d._children ? -6 : 6)
            .attr("text-anchor", d => d._children ? "end" : "start")
            .text(d => d.data.name)
            .style("fill", d => d._children ? LG_GREEN : LG_YELLOW)
            .style("font-family", "'Courier New', monospace")
            .style("text-decoration", "underline")
            .style("font-size", "11px");


        const nodeUpdate = node.merge(nodeEnter).transition(transition)
            .attr("transform", d => `translate(${d.y},${d.x})`)
            .attr("fill-opacity", 1)
            .attr("stroke-opacity", 1);

        const nodeExit = node.exit().transition(transition).remove()
            .attr("transform", d => `translate(${source.y},${source.x})`)
            .attr("fill-opacity", 0)
            .attr("stroke-opacity", 0);

        const link = gLink.selectAll("path")
            .data(links, d => d.target.id);

        const linkEnter = link.enter().append("path")
            .attr("d", d => {
                const o = {x: source.x0, y: source.y0};
                return diagonal({source: o, target: o});
            });

        link.merge(linkEnter).transition(transition)
            .attr("d", diagonal);

        link.exit().transition(transition).remove()
            .attr("d", d => {
                const o = {x: source.x, y: source.y};
                return diagonal({source: o, target: o});
            });

        root.eachBefore(d => {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }

    root.x0 = dy / 2;
    root.y0 = 0;
    root.descendants().forEach((d, i) => {
        d.id = i;
        d._children = d.children;
        if (d.depth && d.data.name.length !== 7) d.children = null;
    });



    update(null, root);

}

fetch('../reports/filesreport_Arquitectura_09_08_21_05.json')
    .then(response => response.json())
    .then(data => draw_tree(data[0]));
