// Minimal DOM-stub harness for prototypes/network_view.html -- verifies autolink() actually
// wraps known mentions in onclick="jumpToNode(...)" links, mirroring wiki_harness.js's own
// check #14 for the live wiki. Written 2026-09-10 after Nick noticed this standalone prototype's
// info-panel prose wasn't linking mentions the way the live wiki does.
const fs = require('fs');

function makeEl(tag) {
  const el = {
    tagName: (tag || 'div').toUpperCase(), children: [], attrs: {}, style: {}, dataset: {},
    innerHTML: '', textContent: '', parentNode: null,
    appendChild(child) { child.parentNode = this; this.children.push(child); return child; },
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k]; },
    addEventListener() {}, removeEventListener() {},
    querySelector() { return null; }, querySelectorAll() { return []; },
    focus() {}, blur() {}, remove() {},
    insertAdjacentHTML(pos, html) { this.innerHTML += html; },
  };
  el.classList = { add() {}, remove() {}, contains() { return false; }, toggle() {} };
  Object.defineProperty(el, 'innerText', { get() { return el.innerHTML.replace(/<[^>]+>/g, ''); } });
  return el;
}

const idMap = {};
global.window = global;
global.document = {
  createElement: (tag) => makeEl(tag),
  createElementNS: (ns, tag) => makeEl(tag),
  getElementById(id) { if (!idMap[id]) idMap[id] = makeEl('div'); idMap[id].id = id; return idMap[id]; },
  querySelectorAll: () => [], querySelector: () => null,
  addEventListener() {}, body: makeEl('body'),
};
global.addEventListener = function () {};
global.requestAnimationFrame = function (cb) { return setTimeout(cb, 0); };
global.matchMedia = function () { return { matches: false }; };
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };

const html = fs.readFileSync(require('path').join(__dirname, '..', '..', 'prototypes', 'network_view.html'), 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('Could not extract <script> block'); process.exit(1); }

try {
  eval(m[1]);
} catch (e) {
  console.error('TOP-LEVEL SCRIPT THREW:', e.stack || e);
  process.exit(1);
}

try {
  selectNode('actor:marwan-barghouti');
  const panelHtml = idMap['infoPanel'].innerHTML;
  const idx = panelHtml.indexOf('Donald Trump');
  console.log('Barghouti panel contains "Donald Trump":', idx !== -1);
  console.log('  is it a jumpToNode link:', /<a onclick="jumpToNode\('actor:donald-trump'\)">Donald Trump<\/a>/.test(panelHtml));
  const wzoIdx = panelHtml.indexOf('Trump');
} catch (e) {
  console.error('SELECTNODE THREW:', e.stack || e);
  process.exit(1);
}

try {
  selectNode('org:world-zionist-organization');
  const panelHtml = idMap['infoPanel'].innerHTML;
  console.log('WZO panel autolinks (has an onclick="jumpToNode(...)" link):', /onclick="jumpToNode\(/.test(panelHtml));
} catch (e) {
  console.error('WZO SELECTNODE THREW:', e.stack || e);
  process.exit(1);
}


function layoutShapeMetrics(nodes, W, H) {
  const xs = nodes.map(n => n.x), ys = nodes.map(n => n.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = x1 - x0, h = y1 - y0;
  let corners = 0, pinned = 0, finite = true;
  nodes.forEach(n => {
    if (!isFinite(n.x) || !isFinite(n.y)) finite = false;
    const fx = (n.x - x0) / w, fy = (n.y - y0) / h;
    if ((fx < 0.12 || fx > 0.88) && (fy < 0.12 || fy > 0.88)) corners++;
    if (n.x <= -449 || n.x >= W + 449 || n.y <= -449 || n.y >= H + 449) pinned++;
  });
  const pts = nodes.map(n => [n.x, n.y]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = []; for (const q of pts) { while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  const up = []; for (const q of pts.slice().reverse()) { while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  const hull = lo.slice(0, -1).concat(up.slice(0, -1));
  const area = Math.abs(hull.reduce((acc, p, i) => { const q = hull[(i + 1) % hull.length]; return acc + p[0] * q[1] - q[0] * p[1]; }, 0)) / 2;
  const rim = nodes.filter(n => Math.hypot((n.x - W / 2) / (W / 2), (n.y - H / 2) / (H / 2)) > 0.97).length;
  return { finite, corners: corners / nodes.length, pinned, rim, fill: area / (w * h) };
}

try {
  const mm = layoutShapeMetrics(nodes, W, H);
  console.log('layout: every node position is a finite number:', mm.finite);
  console.log('layout: no node is flung to the safety clamp:', mm.pinned === 0);
  console.log('layout: corner squares stay (almost) empty (' + (mm.corners * 100).toFixed(1) + '% of nodes):', mm.corners <= 0.03);
  console.log('layout: at most a handful of nodes sit on the outer rim (' + mm.rim + ' nodes):', mm.rim <= 8);
  console.log('layout: hull is not box-shaped (fill ' + mm.fill.toFixed(2) + ' of bounding box):', mm.fill <= 0.9);
} catch (e) {
  console.error('LAYOUT SHAPE CHECK THREW:', e.stack || e);
  process.exit(1);
}

console.log('ALL PROTOTYPE HARNESS CHECKS COMPLETED');
