function extractLeafNodes(tree) {
    const leafNodes = [];
    const leafConections = [];

    function traverse(node) {
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
}


fetch('../reports/filesreport_Arquitectura_09_08_16_17.json')
    .then(res => res.json())
    .then(data => extractLeafNodes(data[0]))
    .then(data => draw_graph(data));/**/
