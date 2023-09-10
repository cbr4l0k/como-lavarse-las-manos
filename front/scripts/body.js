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

function colorin_colorado(st) {
    if (st === "high") {
        return LG_RED;
    } else if (st === 'medium') {
        return LG_ORANGE;
    } else {
        return LG_GREEN;
    }
}

function add_text(data) {
    d3.select("code#desc_eb")
        .datum(data)
        .html(d => { 
            const text =    `<b style='text-decoration: underline;'>Number of Dirs:</b> ${d.directories}<br>` + 
                `<b style='text-decoration: underline;'>Number of Files:</b> ${d.files}<br>` + 
                `<b style='text-decoration: underline;'>Coupling:</b><a style='color: ${colorin_colorado(d.coupling.toLowerCase())};'> ${d.coupling}<a><br>` + 
                `<b style='text-decoration: underline;'>Cohesion:</b><a style='color: ${colorin_colorado(d.cohesion.toLowerCase())};'> ${d.cohesion}<a><br><br>` + `${d.explanation}`
            return text;
        }
        )
}



fetch('../reports/finalreport.json')
    .then(response => response.json())
    .then(data => add_text(data[1]));
