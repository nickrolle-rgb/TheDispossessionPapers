// Minimal DOM-stub harness to actually execute wiki-prototype.html's inline script and verify
// the new routing/popup logic runs without throwing. Not a full browser -- just enough surface
// area for the IIFE to run through its top-level init and the functions we touched this turn.
'use strict';
const fs = require('fs');

function makeEl(tag) {
  const el = {
    tagName: (tag || 'div').toUpperCase(),
    children: [],
    attrs: {},
    style: {},
    dataset: {},
    _listeners: {},
    id: '',
    className: '',
    innerHTML: '',
    textContent: '',
    parentNode: null,
    appendChild(child) { child.parentNode = this; this.children.push(child); return child; },
    removeChild(child) { const i = this.children.indexOf(child); if (i >= 0) this.children.splice(i, 1); child.parentNode = null; return child; },
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k]; },
    addEventListener(type, fn) { (this._listeners[type] = this._listeners[type] || []).push(fn); },
    removeEventListener() {},
    querySelector() { return null; },
    querySelectorAll() { return []; },
    focus() {},
    blur() {},
    remove() { if (this.parentNode) this.parentNode.removeChild(this); },
    insertAdjacentHTML(pos, html) { this.innerHTML += html; },
  };
  const classSet = new Set();
  el.classList = {
    add(...cls) { cls.forEach(c => classSet.add(c)); el.className = Array.from(classSet).join(' '); },
    remove(...cls) { cls.forEach(c => classSet.delete(c)); el.className = Array.from(classSet).join(' '); },
    contains(c) { return classSet.has(c); },
    toggle(c, force) {
      const on = force === undefined ? !classSet.has(c) : force;
      if (on) classSet.add(c); else classSet.delete(c);
      el.className = Array.from(classSet).join(' ');
      return on;
    },
  };
  return el;
}

const idMap = {};
const bodyEl = makeEl('body');

const store = {};
const localStorage = {
  getItem(k) { return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null; },
  setItem(k, v) { store[k] = String(v); },
  removeItem(k) { delete store[k]; },
};

global.window = global;
global.addEventListener = function () {};
global.removeEventListener = function () {};
global.document = {
  createElement(tag) { return makeEl(tag); },
  createElementNS(ns, tag) { const el = makeEl(tag); el._ns = ns; el.setAttribute = function(k, v) { this.attrs[k] = v; }; return el; },
  getElementById(id) {
    if (!idMap[id]) idMap[id] = makeEl('div');
    idMap[id].id = id;
    return idMap[id];
  },
  querySelectorAll() { return []; },
  querySelector() { return null; },
  addEventListener() {},
  body: bodyEl,
  documentElement: makeEl('html'),
};
global.localStorage = localStorage;
global.location = { hash: '', href: 'https://example.test/' };
global.history = { pushState() {}, replaceState() {} };
global.requestAnimationFrame = function (cb) {
  // Run a handful of synchronous "frames" then stop, so any rAF-driven physics loop
  // terminates instead of recursing forever in a fake single-threaded clock.
  global.__rafCount = (global.__rafCount || 0) + 1;
  if (global.__rafCount > 50) return 0;
  setImmediate(() => cb(Date.now()));
  return global.__rafCount;
};
global.cancelAnimationFrame = function () {};
global.matchMedia = function () { return { matches: false, addListener() {}, removeListener() {} }; };
global.scrollTo = function () {};
global.alert = function () {};
global.console = console;

const html = fs.readFileSync(require('path').join(__dirname, '..', '..', 'wiki-prototype.html'), 'utf8');
const m = html.match(/<script>([\s\S]*)<\/script>\s*$/);
if (!m) { console.log('NO SCRIPT MATCH'); process.exit(1); }
let script = m[1];

// Expose internals right before the closing IIFE paren so we can call them directly.
script = script.replace(
  /\}\)\(\);\s*$/,
  `
  global.__net = {
    route: route,
    renderIndex: renderIndex,
    renderNetwork: renderNetwork,
    maybeShowNetworkIntro: maybeShowNetworkIntro,
    dismissNetworkIntro: window.dismissNetworkIntro,
    netBuildGraphData: netBuildGraphData,
    netJumpToNode: netJumpToNode,
    netSelectNode: netSelectNode,
    netClearSelection: window.netClearSelection,
    netZoomBy: window.netZoomBy,
    netResetView: window.netResetView,
    netToggleShowHidden: window.netToggleShowHidden,
    netOnSearchInput: window.netOnSearchInput,
    netOnSearchKeydown: window.netOnSearchKeydown,
    netSearchJump: window.netSearchJump,
    autolink: autolink,
    nameIndex: nameIndex,
    NET: NET,
  };
})();
`
);

try {
  eval(script);
} catch (e) {
  console.error('TOP-LEVEL SCRIPT THREW:', e.stack || e);
  process.exit(1);
}

const net = global.__net;
if (!net) { console.error('harness hook did not attach'); process.exit(1); }

// 1. root route with no hash -> should render Network (front door) and show the intro popup.
try {
  global.location.hash = '';
  net.route();
  const overlay = idMap['netIntroOverlay'];
  console.log('root route -> app innerHTML starts with netview div:', /class="netview"/.test(idMap['app'].innerHTML));
  console.log('intro overlay created on first visit:', !!overlay);
  console.log('intro overlay in body.children:', bodyEl.children.indexOf(overlay) !== -1);
} catch (e) {
  console.error('ROOT ROUTE THREW:', e.stack || e);
  process.exit(1);
}

// 2. dismiss -> localStorage set, overlay removed
try {
  window.dismissNetworkIntro();
  console.log('localStorage flag set after dismiss:', localStorage.getItem('dispossessionpapers-network-intro-seen') === '1');
  console.log('overlay removed from body after dismiss:', !idMap['netIntroOverlay'] || bodyEl.children.indexOf(idMap['netIntroOverlay']) === -1);
} catch (e) {
  console.error('DISMISS THREW:', e.stack || e);
  process.exit(1);
}

// 3. re-route to root again -> popup should NOT reappear (seen flag persists)
try {
  delete idMap['netIntroOverlay'];
  global.location.hash = '';
  net.route();
  console.log('popup does not reappear on second visit:', !idMap['netIntroOverlay'] || bodyEl.children.indexOf(idMap['netIntroOverlay']) === -1);
} catch (e) {
  console.error('SECOND ROOT ROUTE THREW:', e.stack || e);
  process.exit(1);
}

// 4. #/index route -> traditional renderIndex()
try {
  global.location.hash = '#/index';
  net.route();
  console.log('#/index renders traditional index (has index-group):', /class="index-group"/.test(idMap['app'].innerHTML));
  console.log('#/index Actors group folds Foreign (no separate Foreign Patrons heading):', !/Foreign Patrons/.test(idMap['app'].innerHTML));
  console.log('#/index says Organisations (UK spelling):', /Organisations \(/.test(idMap['app'].innerHTML));
} catch (e) {
  console.error('#/index ROUTE THREW:', e.stack || e);
  process.exit(1);
}

// 5. #/network route still works explicitly, has no leftover flip/badge markup
try {
  global.location.hash = '#/network';
  net.route();
  const netHtml = idMap['app'].innerHTML;
  console.log('#/network still renders netview:', /class="netview"/.test(netHtml));
  console.log('#/network has no flip-card markup:', !/net-stage|net-flip|net-index-face/.test(netHtml));
  console.log('#/network has no "Certified library-free" badge:', !/Certified library-free/.test(netHtml));
  console.log('#/network graph pane is present:', /id="netGraphSvg"/.test(netHtml));
} catch (e) {
  console.error('#/network ROUTE THREW:', e.stack || e);
  process.exit(1);
}

// 6. netBuildGraphData sanity, and netJumpToNode selects directly (no flip step to fail on)
try {
  const g = net.netBuildGraphData();
  console.log('netBuildGraphData nodes/edges:', g.nodes.length, g.edges.length);
  net.NET.nodes = g.nodes;
  net.NET.edges = g.edges;
  const someId = g.nodes[0].id;
  net.netJumpToNode(someId);
  console.log('netJumpToNode selects the node directly:', net.NET.selectedId === someId);
} catch (e) {
  console.error('netBuildGraphData/netJumpToNode THREW:', e.stack || e);
  process.exit(1);
}

// 7. every inline onclick/oninput/onkeydown-invoked net* function is actually reachable on window
try {
  const fns = ['netClearSelection','netZoomBy','netResetView','netToggleShowHidden','netOnSearchInput','netOnSearchKeydown','netSearchJump'];
  fns.forEach(name => {
    console.log('window.' + name + ' is a function:', typeof net[name] === 'function');
  });
} catch (e) {
  console.error('WINDOW-EXPOSURE CHECK THREW:', e.stack || e);
  process.exit(1);
}

// 8. netClearSelection actually clears NET.selectedId
try {
  const g = net.netBuildGraphData();
  net.NET.nodes = g.nodes; net.NET.edges = g.edges;
  net.netSelectNode(g.nodes[0].id);
  console.log('netSelectNode set NET.selectedId:', net.NET.selectedId === g.nodes[0].id);
  net.netClearSelection();
  console.log('netClearSelection cleared NET.selectedId:', net.NET.selectedId === null);
} catch (e) {
  console.error('netClearSelection THREW:', e.stack || e);
  process.exit(1);
}

// 9. #/network/<kind>/<id> deep link (what the Index page's links now point at) selects the node
try {
  global.location.hash = '#/network/org/world-zionist-organization';
  net.route();
  console.log('#/network/org/<id> deep link selects that node:', net.NET.selectedId === 'org:world-zionist-organization');
} catch (e) {
  console.error('DEEP LINK ROUTE THREW:', e.stack || e);
  process.exit(1);
}

// 10. WZO / JNF / KKL now survive the length filter and are in the alias index
try {
  const names = net.nameIndex.map(n => n.name);
  console.log('WZO in nameIndex:', names.includes('WZO'));
  console.log('JNF in nameIndex:', names.includes('JNF'));
  console.log('KKL in nameIndex:', names.includes('KKL'));
  const linked = net.autolink('The WZO convened in Basel.', null);
  console.log('WZO actually autolinks in prose:', /<a [^>]*>WZO<\/a>/.test(linked));
} catch (e) {
  console.error('ALIAS CHECK THREW:', e.stack || e);
  process.exit(1);
}

// 11. #/index links now point into #/network/<kind>/<id>, not the old dedicated-page hrefs
try {
  global.location.hash = '#/index';
  net.route();
  const idxHtml = idMap['app'].innerHTML;
  console.log('#/index actor links point at #/network/actor/...:', /#\/network\/actor\//.test(idxHtml));
  console.log('#/index org links point at #/network/org/...:', /#\/network\/org\//.test(idxHtml));
  console.log('#/index no longer emits old #/actor/ or #/org/ hrefs:', !/href="#\/actor\//.test(idxHtml) && !/href="#\/org\//.test(idxHtml));
} catch (e) {
  console.error('INDEX LINK CHECK THREW:', e.stack || e);
  process.exit(1);
}

// 12. Laws/Topics merge: #/index shows a merged "Legislation" heading (Laws + bills/resolutions),
// no separate laws-only heading, and Legislative Proposal/UN Resolution nodes classify as "law"
try {
  global.location.hash = '#/index';
  net.route();
  const idxHtml = idMap['app'].innerHTML;
  console.log('#/index has a "Legislation" heading:', /Legislation \(/.test(idxHtml));
  console.log('#/index has no separate "Laws (" heading:', !/>Laws \(/.test(idxHtml));
  const g = net.netBuildGraphData();
  const resolution181 = g.nodes.find(n => n.id === 'topic:resolution-181');
  const jordanValleyBill = g.nodes.find(n => n.id === 'topic:jordan-valley-sovereignty-bill-2023');
  console.log('UN Resolution 181 node classifies as kind "law":', resolution181 && resolution181.kind === 'law');
  console.log('Jordan Valley Sovereignty Bill node classifies as kind "law":', jordanValleyBill && jordanValleyBill.kind === 'law');
  const icjOpinion = g.nodes.find(n => n.id === 'topic:icj-advisory-opinion-2024');
  const icjCase = g.nodes.find(n => n.id === 'topic:south-africa-v-israel-icj');
  console.log('ICJ Advisory Opinion node classifies as kind "law":', icjOpinion && icjOpinion.kind === 'law');
  console.log('South Africa v. Israel ICJ Case node classifies as kind "law":', icjCase && icjCase.kind === 'law');
  const iccSituation = g.nodes.find(n => n.id === 'topic:icc-situation-in-palestine');
  console.log('ICC Situation in Palestine node classifies as kind "law":', iccSituation && iccSituation.kind === 'law');
} catch (e) {
  console.error('LEGISLATION MERGE CHECK THREW:', e.stack || e);
  process.exit(1);
}

// 13. stamps are plain text, not links (no href, no navigation) -- the fishhook, not the answer
try {
  global.location.hash = '#/network';
  net.route();
  const netHtml = idMap['app'].innerHTML;
  console.log('stamps present as plain span (no href):', /<span class="net-stamp-tag"[^>]*>Reinstate Resolution 3379<\/span>/.test(netHtml));
  console.log('no stamp <a href> remains:', !/net-stamp-tag" [^>]*href/.test(netHtml));
} catch (e) {
  console.error('STAMP CHECK THREW:', e.stack || e);
  process.exit(1);
}

// 14. network info panel prose now autolinks known mentions into #/network/<kind>/<id>
try {
  const g = net.netBuildGraphData();
  net.NET.nodes = g.nodes; net.NET.edges = g.edges;
  // World Zionist Organization's own role/events should mention other profiled figures/orgs
  const wzo = g.nodes.find(n => n.id === 'org:world-zionist-organization');
  net.netSelectNode('org:world-zionist-organization');
  const panelHtml = idMap['netInfoPanel'].innerHTML;
  console.log('WZO panel found:', !!wzo);
  console.log('network info panel prose contains a #/network/ autolink:', /href="#\/network\//.test(panelHtml));
} catch (e) {
  console.error('INFO PANEL AUTOLINK CHECK THREW:', e.stack || e);
  process.exit(1);
}

// 14b. Debug: does Barghouti's own "Donald Trump's Gaza peace plan" text actually autolink "Donald Trump"?
try {
  net.netSelectNode('actor:marwan-barghouti');
  const panelHtml = idMap['netInfoPanel'].innerHTML;
  const idx = panelHtml.indexOf('Donald Trump');
  console.log('Barghouti panel contains "Donald Trump":', idx !== -1);
  if (idx !== -1) console.log('  context:', panelHtml.slice(Math.max(0, idx - 80), idx + 20).replace(/\n/g, ' '));
} catch (e) {
  console.error('BARGHOUTI AUTOLINK DEBUG THREW:', e.stack || e);
}

// 15. mobile info-panel sizing hook: netInfoPanelWrap gets .has-selection on select, loses it on clear
try {
  net.netSelectNode('org:world-zionist-organization');
  const wrap = idMap['netInfoPanelWrap'];
  console.log('netInfoPanelWrap gains has-selection on select:', !!wrap && wrap.classList.contains('has-selection'));
  net.netClearSelection();
  console.log('netInfoPanelWrap loses has-selection on clear:', !!wrap && !wrap.classList.contains('has-selection'));
} catch (e) {
  console.error('MOBILE INFO-PANEL SIZING CHECK THREW:', e.stack || e);
  process.exit(1);
}

console.log('ALL HARNESS CHECKS COMPLETED');

// 16. Dump the wiki's own graph edges (unique source|target|kind) for the edge-parity diff against the
// Python-built prototype. Written to OUT_DIR (env SCRATCH_DIR, else this folder).
try {
  const g = net.netBuildGraphData();
  const lines = Array.from(new Set(g.edges.map(e => e.source + '|' + e.target + '|' + e.kind))).sort();
  const outDir = process.env.SCRATCH_DIR || __dirname;
  fs.writeFileSync(require('path').join(outDir, 'js_edges.txt'), lines.join('\n'));
  console.log('unique js edges:', lines.length);
} catch (e) {
  console.error('EDGE DUMP THREW:', e.stack || e);
  process.exit(1);
}
