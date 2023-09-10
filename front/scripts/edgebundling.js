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

function extractLeafNodes(tree) {
    console.log(tree)
    const leafNodes = [];
    const leafConections = [];

    function traverse(node) {
        // console.log(node);
        if (!node.children || node.children.length === 0) {
            const { full_path, ...newNode } = node;
            const updatedNode = { ...newNode, id: full_path };


            const links = updatedNode.dependencies.map( elem =>{
                return {
                    source: full_path, target: elem
                }
            });
            leafConections.push(...links);
            leafNodes.push(updatedNode);
            return;
        }
        for (const child of node.children) {
            traverse(child);
        }
    }

    traverse(tree);

    return {
        nodes: leafNodes,
        links: leafConections,
    };
}



function draw_graph(data) {
    // console.log(data);
    // Random tree
    const N = 300;
    const gData = {
      nodes: [...Array(N).keys()].map(i => ({
          id: i,
          times_called: Math.round(Math.random() * (i-1)),
      })),
      links: [...Array(N).keys()]
        .filter(id => id)
        .map(id => ({
          source: id,
          target: Math.round(Math.random() * (id-1))
        }))
    };

    const Graph = ForceGraph3D({
      times_called: [new CSS2DRenderer()]
    })
      (document.getElementById('container_eb'))
        .graphData(gData)
        .backgroundColor(DK_BG)
        .nodeVal('times_called')
        .nodeLabel('id')
        .nodeThreeObject(node => {
            console.log(node)
            const nodeEl = document.createElement('div');
            nodeEl.textContent = `uWu ${node.id}`;
            nodeEl.style.color = node.color;
            nodeEl.className = 'node-label';
            return new CSS2DObject(nodeEl);
        })
        .nodeThreeObjectExtend(true)

}


fetch('../reports/filesreport_Arquitectura_09_08_21_05.json')
    .then(res => res.json())
    .then(data => extractLeafNodes(data[0]))
    .then(data => draw_graph(data));/**/
