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
    const leafNodes = [];
    const leafConections = [];

    function traverse(node) {
        console.log(node);
        if (!node.children || node.children.length === 0) {
            const { full_path, ...newNode } = node;
            const updatedNode = { ...newNode, id: full_path };


            const links = updatedNode.dependencies.map( elem =>{
                console.log(elem)
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
    console.log(data);
    // Random tree
    const N = 300;
    const gData = {
      nodes: [...Array(N).keys()].map(i => ({ id: i })),
      links: [...Array(N).keys()]
        .filter(id => id)
        .map(id => ({
          source: id,
          target: Math.round(Math.random() * (id-1))
        }))
    };

    const Graph = ForceGraph3D()
      (document.getElementById('container_eb'))
        .graphData(gData)
        .nodeColor("#ffffff")
        .backgroundColor(DK_BG);
    console.log("#ffffff")
}


fetch('../reports/filesreport_Arquitectura_09_08_16_17.json')
    .then(res => res.json())
    .then(data => extractLeafNodes(data[0]))
    .then(data => draw_graph(data));/**/
