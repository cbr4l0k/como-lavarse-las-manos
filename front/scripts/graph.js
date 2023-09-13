import { CSS2DRenderer, CSS2DObject } from '//unpkg.com/three/examples/jsm/renderers/CSS2DRenderer.js';

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

const BLACKLIST =  [
    // "int/abc",
]

/**
 * This function traverses the provided tree structure and extracts leaf nodes.
 * It also gathers connections between nodes.
 * @param {Object} tree - The root of the tree to be traversed.
 * @returns {Object} - An object containing an array of leaf nodes and their connections.
 */
function extractLeafNodes(tree) {
    const leafNodes = [];
    const leafConections = [];

    function traverse(node) {
        if ( !node.hasOwnProperty('dependencies')) {
            if (node.type === "directory") {
                for (const child of node.children) {
                    traverse(child);
                }

            }
            return;
        }
        if (!node.children || node.children.length === 0 ) {
            if (node.type === "External dependency") {
                node.id = node.name
            }

            const links = node.dependencies.map( elem =>{
                if (BLACKLIST.indexOf(elem) > -1) {
                    return ;
                } else {
                    const D = {
                        target: node.id , source: elem
                    }
                    return D;
                }
            });
            leafConections.push(...links);
            leafNodes.push(node);
            return;

        }
        for (const child of node.children) {
            traverse(child);
        }
    }

    traverse(tree);
    const obj = {
        nodes: leafNodes,
        links: leafConections.filter(item => item !== undefined),
    };
    return obj;
}



/**
 * This function uses the provided graph data to draw a 3D force graph.
 * @param {Object} gData - Graph data containing nodes and their connections.
 */
function draw_graph(gData) {


    // cross-link node objects
    gData.links.forEach(link => {
        const a = gData.nodes[gData.nodes.findIndex(item => {
            return link.source === item.id;
        })];
        const b = gData.nodes[gData.nodes.findIndex(item => {
            return link.target === item.id;
        })];

        !a.neighbors && (a.neighbors = []);
        !b.neighbors && (b.neighbors = []);
        a.neighbors.push(b);
        b.neighbors.push(a);

        !a.links && (a.links = []);
        !b.links && (b.links = []);
        a.links.push(link);
        b.links.push(link);
    });

    const highlightNodes = new Set();
    const highlightLinks = new Set();
    let hoverNode = null;

    const container = document.getElementById('container_eb');

    const height = window.screen.availHeight * 0.41;
    const width = window.screen.availWidth * 0.59;

    const Graph = ForceGraph3D({times_called:[new CSS2DRenderer()]})(container)
        .width(width)
        .height(height)
        .graphData(gData)
        .backgroundColor(DK_BG)
        .nodeVal('times_called')
        .nodeLabel('name')
        .nodeColor(node => highlightNodes.has(node) ? node === hoverNode ? LG_GREEN : LG_YELLOW : LG_GRAY)
        .linkWidth(link => highlightLinks.has(link) ? 4 : 1)
        .linkDirectionalParticles(link => highlightLinks.has(link) ? 4 : 0)
        .linkDirectionalParticleWidth(4)
        .onNodeHover(node => {
            // no state change
            if ((!node && !highlightNodes.size) || (node && hoverNode === node)) return;

            highlightNodes.clear();
            highlightLinks.clear();
            if (node) {
                highlightNodes.add(node);
                node.neighbors.forEach(neighbor => highlightNodes.add(neighbor));
                node.links.forEach(link => highlightLinks.add(link));
            }

            hoverNode = node || null;

            updateHighlight();
        })
        .onLinkHover(link => {
            highlightNodes.clear();
             highlightLinks.clear();

            if (link) {
                highlightLinks.add(link);
                highlightNodes.add(link.source);
                highlightNodes.add(link.target);
            }

            updateHighlight();
        });

    function updateHighlight() {
        // trigger update of highlighted objects in scene
        Graph
            .nodeColor(Graph.nodeColor())
            .linkWidth(Graph.linkWidth())
            .linkDirectionalParticles(Graph.linkDirectionalParticles());
    }

}

// Fetch data from a JSON file, extract leaf nodes, and draw the graph
fetch('../reports/finalreport.json')
    .then(res => res.json())
    .then(data => extractLeafNodes(data[0]))
    .then(data => draw_graph(data))
