// Offline lab for the network map's force layout: runs the same physics as wiki-prototype.html's netInit()
// (and the standalone prototype's simulate()) against the real graph, with a SEEDED random number generator
// so runs are comparable, and prints "boxiness" metrics. Optionally writes an SVG preview.
//
//   node scripts/layout_lab.js                         baseline (current production physics)
//   node scripts/layout_lab.js --variant=organic       a candidate
//   node scripts/layout_lab.js --variant=organic --svg=preview.svg --seed=7
//
// Metrics (lower is better unless noted):
//   edgeHug   share of nodes sitting in the outer 4% band of the bounding box (nodes "right along the edge")
//   corners   share of nodes inside the four corner squares (12% of each side)
//   fill      convex-hull area / bounding-box area (HIGHER = boxier, a blob scores lower; a rectangle scores ~1)
//   minGap    smallest centre-to-centre distance between any two nodes (overlap risk; bigger is safer)
'use strict';
const fs = require('fs');
const path = require('path');

const args = Object.fromEntries(process.argv.slice(2).map(a => a.replace(/^--/, '').split('=')));
const variant = args.variant || 'baseline';
const seed = Number(args.seed || 1);

// ---- load the real graph from the built prototype ----
const html = fs.readFileSync(path.join(__dirname, '..', 'prototypes', 'network_view.html'), 'utf8');
const line = html.split('\n').find(l => l.startsWith('var GRAPH_DATA = '));
const data = JSON.parse(line.slice('var GRAPH_DATA = '.length).replace(/;\s*$/, ''));

// ---- seeded RNG (mulberry32) ----
let s = seed >>> 0;
function rnd() { s |= 0; s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }

const NET_W = 4800, NET_H = 3900;
const CLUSTER = { right: 1, left: 1, religious: 1, centrist: 1 };

function build() {
  const nodes = data.nodes.map(n => {
    const col = ({ actor: 0.22, mk: 0.78, org: 0.5, law: 0.5, topic: 0.5, foreign: 0.9 }[n.kind]) || 0.5;
    const row = ({ actor: 0.25, mk: 0.25, org: 0.55, law: 0.8, topic: 0.65, foreign: 0.5 }[n.kind]) || 0.5;
    return { id: n.id, kind: n.kind, label: n.label || '', align: n.align || 'unaffiliated',
      x: NET_W * col + (rnd() - 0.5) * 960, y: NET_H * row + (rnd() - 0.5) * 960, vx: 0, vy: 0, degree: 0 };
  });
  const byId = {}; nodes.forEach(n => { byId[n.id] = n; });
  const edges = data.edges.map(e => { byId[e.source].degree++; byId[e.target].degree++; return { source: byId[e.source], target: byId[e.target] }; });
  return { nodes, edges, byId };
}

// connected components (union-find) -> comp size per node
function components(nodes, edges) {
  const parent = new Map(nodes.map(n => [n.id, n.id]));
  const find = x => { while (parent.get(x) !== x) { parent.set(x, parent.get(parent.get(x))); x = parent.get(x); } return x; };
  edges.forEach(e => { const a = find(e.source.id), b = find(e.target.id); if (a !== b) parent.set(a, b); });
  const size = new Map();
  nodes.forEach(n => { const r = find(n.id); size.set(r, (size.get(r) || 0) + 1); });
  let max = 0; size.forEach(v => { if (v > max) max = v; });
  nodes.forEach(n => { n.comp = find(n.id); n.compSize = size.get(n.comp); });
  return max;
}


// Approximate the on-screen footprint of a node: its dot plus its text label, which runs to the right of the dot.
const CH = 11, PAD = 40;
function boxOf(n) { const lw = Math.min(n.label.length, 46) * CH; return { x0: n.x - 24, x1: n.x + 24 + lw, y0: n.y - 26, y1: n.y + 26 }; }
function hit(a, b, pad) { return a.x0 < b.x1 + pad && a.x1 > b.x0 - pad && a.y0 < b.y1 + pad && a.y1 > b.y0 - pad; }

function simulate(g, v) {
  const { nodes, edges } = g;
  const mainSize = components(nodes, edges);
  for (let it = 0; it < 420; it++) {
    for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      const dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy || 0.01, d = Math.sqrt(d2);
      const force = 41400 / d2, fx = dx / d * force, fy = dy / d * force;
      a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy;
      if (a.align === b.align && CLUSTER[a.align]) {
        const cf = Math.min(d, 1560) * 0.00018;
        a.vx -= dx / d * cf; a.vy -= dy / d * cf; b.vx += dx / d * cf; b.vy += dy / d * cf;
      }
    }
    edges.forEach(e => {
      const dx = e.target.x - e.source.x, dy = e.target.y - e.source.y, d = Math.sqrt(dx * dx + dy * dy) || 0.01;
      const force = (d - 168) * 0.02, fx = dx / d * force, fy = dy / d * force;
      e.source.vx += fx; e.source.vy += fy; e.target.vx -= fx; e.target.vy -= fy;
    });
    nodes.forEach(n => {
      let gm = 1;
      if (v.islandGravity) gm = 1 + v.islandGravity * (1 - Math.sqrt(n.compSize / mainSize)); // small components get pulled in
      n.vx += (NET_W / 2 - n.x) * 0.0004 * gm; n.vy += (NET_H / 2 - n.y) * 0.0004 * gm;
      if (v.ellipse) {
        // soft elliptical containment instead of four straight walls: no corners to pile into
        const rx = NET_W * v.ellipse, ry = NET_H * v.ellipse;
        const ex = (n.x - NET_W / 2) / rx, ey = (n.y - NET_H / 2) / ry, r = Math.sqrt(ex * ex + ey * ey);
        if (r > 1) { const k = (r - 1) * 0.6; n.vx -= (ex / r) * k * rx * 0.05; n.vy -= (ey / r) * k * ry * 0.05; }
      } else {
        const m = 255;
        if (n.x < m) n.vx += (m - n.x) * 0.03; if (n.x > NET_W - m) n.vx -= (n.x - (NET_W - m)) * 0.03;
        if (n.y < m) n.vy += (m - n.y) * 0.03; if (n.y > NET_H - m) n.vy -= (n.y - (NET_H - m)) * 0.03;
      }
      n.vx += (rnd() - 0.5) * 0.12; n.vy += (rnd() - 0.5) * 0.12;
    });
    nodes.forEach(n => {
      n.vx *= 0.82; n.vy *= 0.82; n.x += n.vx; n.y += n.vy;
      n.x = Math.max(-450, Math.min(NET_W + 450, n.x)); n.y = Math.max(-450, Math.min(NET_H + 450, n.y));
    });
  }
}


// ---- post-pass: move nodes/clusters that ended up hugging the outer edge into genuinely empty space ----
// Outer nodes are grouped by connectivity among themselves, so a pendant cluster hanging off the main mass on a long
// edge (or a lone isolated node) moves as one rigid piece. Each group is dropped into the nearest gap, near whatever
// it is attached to, that has clearance for every member's dot and label.
function tuck(g, opts) {
  const { nodes, edges } = g;
  const xs = nodes.map(n => n.x), ys = nodes.map(n => n.y);
  const q = (arr, p) => arr.slice().sort((a, b) => a - b)[Math.max(0, Math.min(arr.length - 1, Math.floor(p * arr.length)))];
  const cx = q(xs, 0.5), cy = q(ys, 0.5);
  const x0 = q(xs, 0.03), x1 = q(xs, 0.97), y0 = q(ys, 0.03), y1 = q(ys, 0.97);
  const rx = (x1 - x0) / 2, ry = (y1 - y0) / 2;
  const rad = n => Math.hypot((n.x - cx) / rx, (n.y - cy) / ry);
  const shell = opts.shell || 0.9, inner = opts.inner || 0.85, pad = opts.pad === undefined ? 30 : opts.pad;
  const outer = new Set(nodes.filter(n => rad(n) > shell).map(n => n.id));
  // connected components of the subgraph induced by outer nodes
  const adj = new Map(nodes.map(n => [n.id, []]));
  edges.forEach(e => { adj.get(e.source.id).push(e.target); adj.get(e.target.id).push(e.source); });
  const seen = new Set(), groups = [];
  nodes.forEach(n => {
    if (!outer.has(n.id) || seen.has(n.id)) return;
    const grp = [], stack = [n]; seen.add(n.id);
    while (stack.length) { const c = stack.pop(); grp.push(c); adj.get(c.id).forEach(m => { if (outer.has(m.id) && !seen.has(m.id)) { seen.add(m.id); stack.push(m); } }); }
    groups.push(grp);
  });
  groups.sort((a, b) => b.length - a.length);
  const moved = [];
  groups.forEach(members => {
    const ids = new Set(members.map(m => m.id));
    const gx = members.reduce((t, m) => t + m.x, 0) / members.length, gy = members.reduce((t, m) => t + m.y, 0) / members.length;
    const ext = [];
    members.forEach(m => adj.get(m.id).forEach(nb => { if (!ids.has(nb.id)) ext.push(nb); }));
    const anchor = ext.length ? [ext.reduce((t, m) => t + m.x, 0) / ext.length, ext.reduce((t, m) => t + m.y, 0) / ext.length] : [gx, gy];
    const otherBoxes = nodes.filter(n => !ids.has(n.id)).map(boxOf);
    let best = null, bestScore = Infinity;
    // try the roomiest placement first, then progressively accept tighter gaps and a larger reach
    for (const [innerR, padV] of [[inner, pad], [inner + 0.1, Math.round(pad / 2)], [inner + 0.2, 0]]) {
      for (let t = 0; t < 4000; t++) {
        const ang = rnd() * Math.PI * 2, rr = Math.sqrt(rnd()) * innerR;
        const px = cx + Math.cos(ang) * rr * rx, py = cy + Math.sin(ang) * rr * ry;
        const dx = px - gx, dy = py - gy;
        let ok = true;
        for (const m of members) {
          const nm = { x: m.x + dx, y: m.y + dy, label: m.label };
          if (Math.hypot((nm.x - cx) / rx, (nm.y - cy) / ry) > innerR + 0.05) { ok = false; break; }
          const b = boxOf(nm);
          for (const ob of otherBoxes) if (hit(b, ob, padV)) { ok = false; break; }
          if (!ok) break;
        }
        if (!ok) continue;
        const score = Math.hypot(px - anchor[0], py - anchor[1]);
        if (score < bestScore) { bestScore = score; best = [dx, dy]; }
      }
      if (best) break;
    }
    if (!best) {
      // dense surroundings: slide the group inward from where it is, along several headings, and keep the deepest
      // position that is still collision-free
      const fits = (dx, dy, padv) => members.every(m => { const b = boxOf({ x: m.x + dx, y: m.y + dy, label: m.label }); return !otherBoxes.some(ob => hit(b, ob, padv)); });
      const meanR = (dx, dy) => members.reduce((t, m) => t + Math.hypot((m.x + dx - cx) / rx, (m.y + dy - cy) / ry), 0) / members.length;
      let bestR = meanR(0, 0) - 0.05;
      const base = Math.atan2(cy - gy, cx - gx);
      for (let k = -8; k <= 8; k++) {
        const ang = base + k * 0.11, ux = Math.cos(ang), uy = Math.sin(ang);
        let last = null;
        for (let d = 30; d < 3500; d += 30) { if (fits(ux * d, uy * d, 12)) last = [ux * d, uy * d]; else if (last) break; }
        if (last) { const r = meanR(last[0], last[1]); if (r < bestR) { bestR = r; best = last; } }
      }
    }
    if (best) { members.forEach(m => { m.x += best[0]; m.y += best[1]; }); moved.push(members.length); }
    else {
      moved.push(-members.length); // could not be placed (negative = left where it was)
      if (opts.debug) {
        const mx0 = Math.min(...members.map(m => m.x)), mx1 = Math.max(...members.map(m => m.x)), my0 = Math.min(...members.map(m => m.y)), my1 = Math.max(...members.map(m => m.y));
        console.log('  unplaced group of ' + members.length + ' extent ' + Math.round(mx1 - mx0) + 'x' + Math.round(my1 - my0) + ' r~' + (members.reduce((t, m) => t + rad(m), 0) / members.length).toFixed(2) + ': ' + members.slice(0, 6).map(m => m.id.split(':')[1].slice(0, 22)).join(', '));
      }
    }
  });
  return moved;
}

function hull(points) {
  const p = points.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = []; for (const q of p) { while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  const up = []; for (const q of p.slice().reverse()) { while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
const area = poly => Math.abs(poly.reduce((acc, p, i) => { const q = poly[(i + 1) % poly.length]; return acc + p[0] * q[1] - q[0] * p[1]; }, 0)) / 2;

function metrics(nodes) {
  const xs = nodes.map(n => n.x), ys = nodes.map(n => n.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = x1 - x0, h = y1 - y0;
  const band = 0.04, cs = 0.12;
  let hug = 0, corner = 0;
  nodes.forEach(n => {
    const fx = (n.x - x0) / w, fy = (n.y - y0) / h;
    if (fx < band || fx > 1 - band || fy < band || fy > 1 - band) hug++;
    if ((fx < cs || fx > 1 - cs) && (fy < cs || fy > 1 - cs)) corner++;
  });
  let minGap = Infinity;
  for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) minGap = Math.min(minGap, Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y));
  let pinned = 0;
  nodes.forEach(n => { if (n.x <= -449 || n.x >= NET_W + 449 || n.y <= -449 || n.y >= NET_H + 449) pinned++; });
  const boxes = nodes.map(boxOf); let overlaps = 0;
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) if (hit(boxes[i], boxes[j], 0)) overlaps++;
  return { bbox: [Math.round(w), Math.round(h)], pinned, overlaps, edgeHug: +(hug / nodes.length).toFixed(3), corners: +(corner / nodes.length).toFixed(3),
    fill: +(area(hull(nodes.map(n => [n.x, n.y]))) / (w * h)).toFixed(3), minGap: Math.round(minGap), n: nodes.length };
}

const VARIANTS = {
  baseline: {},
  island: { islandGravity: 6 },
  ellipse: { ellipse: 0.5 },
  organic: { islandGravity: 6, ellipse: 0.5 },
  tuck: { tuck: true },
  organicTuck: { islandGravity: 4, ellipse: 0.5, tuck: true },
};
const g = build();
const V = VARIANTS[variant] || {};
simulate(g, V);
let movedInfo = '';
if (V.tuck) { const mv = tuck(g, Object.assign({ debug: !!args.debug }, V)); movedInfo = ' moved ' + mv.filter(x => x > 0).length + ' groups (' + mv.filter(x => x > 0).reduce((a, b) => a + b, 0) + ' nodes), unplaced ' + mv.filter(x => x < 0).length; }
const m = metrics(g.nodes);
if (args.stragglers) {
  const xs = g.nodes.map(n => n.x).sort((a, b) => a - b), ys = g.nodes.map(n => n.y).sort((a, b) => a - b);
  const qq = (arr, p) => arr[Math.floor(p * (arr.length - 1))];
  const cx = qq(xs, 0.5), cy = qq(ys, 0.5), rx = (qq(xs, 0.97) - qq(xs, 0.03)) / 2, ry = (qq(ys, 0.97) - qq(ys, 0.03)) / 2;
  components(g.nodes, g.edges);
  g.nodes.map(n => ({ n, r: Math.hypot((n.x - cx) / rx, (n.y - cy) / ry) })).filter(o => o.r > 0.92).sort((a, b) => b.r - a.r).slice(0, 30)
    .forEach(o => console.log('  r=' + o.r.toFixed(2), o.n.kind, 'deg', o.n.degree, 'comp', o.n.compSize, o.n.id.slice(0, 50)));
}
console.log(variant, 'seed', seed, JSON.stringify(m) + movedInfo);

if (args.svg) {
  const xs = g.nodes.map(n => n.x), ys = g.nodes.map(n => n.y);
  const x0 = Math.min(...xs) - 80, y0 = Math.min(...ys) - 80, w = Math.max(...xs) - x0 + 80, h = Math.max(...ys) - y0 + 80;
  const col = { right: '#e07354', left: '#7fa294', religious: '#d9a441', centrist: '#2f7dd1' };
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${x0} ${y0} ${w} ${h}" style="background:#171e22">`;
  g.edges.forEach(e => { svg += `<line x1="${e.source.x}" y1="${e.source.y}" x2="${e.target.x}" y2="${e.target.y}" stroke="#8b8879" stroke-opacity=".35" stroke-width="3"/>`; });
  g.nodes.forEach(n => { svg += `<circle cx="${n.x}" cy="${n.y}" r="${6 + Math.min(n.degree, 20) * 1.2}" fill="${col[n.align] || '#8b8879'}"/>`; });
  svg += '</svg>';
  fs.writeFileSync(path.resolve(args.svg), svg);
  console.log('wrote', args.svg);
}
