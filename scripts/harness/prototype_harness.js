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

console.log('ALL PROTOTYPE HARNESS CHECKS COMPLETED');
