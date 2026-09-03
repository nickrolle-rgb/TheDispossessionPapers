#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds prototypes/network_view.html from the live data files and
prototypes/network_view_template.html.

This is the design-prototype counterpart to scripts/embed_data.py: same idea (curated JSON ->
one self-contained HTML file), different output -- an interactive force-directed graph of every
Actor, Knesset Member, Organization, Law, and Topic, instead of the article-per-page wiki.

Not wired into wiki-prototype.html yet. Kept here, with real edges and a real (if approximate)
political-alignment classifier, so a future session can pick this up without reconstructing it
from scratch, and so its own logic (the alignment classifier especially) is reviewable and
version-controlled rather than living only in an ephemeral Claude-side scratchpad.

Usage:
    python prototypes/build_network_view.py
"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = Path(__file__).resolve().parent / "network_view_template.html"
OUTPUT_PATH = Path(__file__).resolve().parent / "network_view.html"


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


actors = load("historical_actors.json")
mks = load("knesset_members.json")
orgs = load("organizations.json")
laws = load("laws.json")
topics = load("topics.json")
foreign = load("current_foreign_actors.json")

# ---------- political-alignment classification (drives node colour; shape encodes kind) ----------
RIGHT_KW = ["revisionist", "greater israel", "territorial maximalism", "national conservatism",
            "iron wall", "neo-zionism", "hadar", "monistic", "free-market", "anti-british revolt",
            "kahanism", "ultranationalism", "far-right", "settlement expansion"]
LEFT_KW = ["labor zionism", "socialist zionism", "social democracy", "marxist", "trade unionism",
           "religion of labor", "gordonism", "pragmatic statism"]
RELIGIOUS_KW = ["religious zionism"]

# Government offices, sovereign/legislative bodies, foreign/international bodies, and
# financial/land-holding institutions serve (or represent) the whole system, not one political
# camp -- an ideology-keyword or lineage match should never override this. This is the "could
# change hands" test (Nick, 2026-09-03): a Prime Minister's office is institutional regardless of
# who currently holds it; Kadima is not, even though its own ideology tag ("Centrist") doesn't
# keyword-match -- it resolves via lineage propagation below instead.
INSTITUTIONAL_TYPES = {
    "Government Office", "Legislative Body", "Sovereign State", "Self-Governing Community",
    "National Military", "International Body", "Representative Assembly", "Executive Council",
    "International Zionist Body", "Financial Institution", "Land Fund", "Land Company",
}

def ideology_match(ideology_list):
    text = " | ".join(ideology_list).lower()
    if any(k in text for k in RELIGIOUS_KW):
        return "religious"
    if any(k in text for k in RIGHT_KW):
        return "right"
    if any(k in text for k in LEFT_KW):
        return "left"
    return None

org_by_id = {o["org_id"]: o for o in orgs}
org_alignment = {}
for o in orgs:
    if o.get("org_type") in INSTITUTIONAL_TYPES:
        org_alignment[o["org_id"]] = "institutional"
    else:
        org_alignment[o["org_id"]] = ideology_match(o.get("ideology", []))  # may be None for now

# Lineage propagation: an org with no direct ideology match inherits its neighbour's *resolved*
# colour across predecessor/successor/merged_into edges -- but only from a neighbour that
# resolved to an actual political colour, never an institutional one, so a party doesn't pick up
# "institutional" just for once having passed through state machinery. Free-text lineage entries
# like "Hovevei Zion (informal predecessor...)" are skipped -- same guard collision_check.py uses.
def lineage_neighbors(org):
    lin = org.get("lineage", {}) or {}
    ids = list(lin.get("predecessor_orgs", []) or []) + list(lin.get("successor_orgs", []) or [])
    mi = lin.get("merged_into")
    if mi:
        ids.append(mi)
    return [i for i in ids if i in org_by_id]

for _pass in range(4):  # a few passes lets a resolved colour propagate down a short chain
    changed = False
    for o in orgs:
        oid = o["org_id"]
        if org_alignment[oid] is not None:
            continue
        for nid in lineage_neighbors(o):
            if org_alignment.get(nid) in ("right", "left", "religious"):
                org_alignment[oid] = org_alignment[nid]
                changed = True
                break
    if not changed:
        break

# Anything still unresolved (a real proto-movement or non-Zionist party with no keyword match and
# no coloured lineage neighbour -- Hovevei Zion, United Torah Judaism) is honestly "no data", not
# folded into "institutional" as a catch-all.
for oid in org_alignment:
    if org_alignment[oid] is None:
        org_alignment[oid] = "unaffiliated"

# ---------- nodes ----------
nodes = []
node_index = {}

def add_node(id_, kind, label, detail):
    node_index[id_] = len(nodes)
    nodes.append({"id": id_, "kind": kind, "label": label, "detail": detail, "align": None})

for a in actors:
    life = a.get("life_span", {}) or {}
    lifestr = f"{life.get('born','?')}–{life.get('died') or 'present'}"
    add_node("actor:" + a["actor_id"], "actor", a["full_name"], {
        "meta": lifestr, "role": a.get("historical_role", ""),
        "events": [{"when": e.get("date",""), "what": e.get("action_type",""), "text": e.get("impact_description","")}
                   for e in a.get("key_land_actions", [])],
        "personal": [{"title": p.get("title",""), "when": p.get("date_or_range",""), "text": p.get("description","")}
                     for p in a.get("personal_context", [])],
    })

for m in mks:
    terms = m.get("knesset_terms", []) or []
    partystr = ", ".join(sorted({t.get("party","") for t in terms if t.get("party")})) or "party affiliation not recorded"
    add_node("mk:" + m["mk_id"], "mk", m["full_name"], {
        "meta": f"Knesset Member · {partystr}", "role": "",
        "events": [{"when": e.get("date",""), "what": e.get("bill_or_action_title",""),
                    "text": (e.get("land_impact") or {}).get("description","") + f" ({e.get('vote','')})"}
                   for e in m.get("legislative_and_action_record", [])],
        "personal": [{"title": p.get("title",""), "when": p.get("date_or_range",""), "text": p.get("description","")}
                     for p in m.get("personal_context", [])],
    })

for o in orgs:
    dates = o.get("founding_date","?") + (f" – {o['dissolution_date']}" if o.get("dissolution_date") else " – present")
    add_node("org:" + o["org_id"], "org", o["name"], {
        "meta": f"{o.get('org_type','')} · {dates}", "role": ", ".join(o.get("ideology", [])),
        "events": [{"when": e.get("date",""), "what": e.get("title",""), "text": e.get("description","")}
                   for e in o.get("action_record", [])],
        "personal": [],
    })
    nodes[node_index["org:" + o["org_id"]]]["align"] = org_alignment[o["org_id"]]

for l in laws:
    add_node("law:" + l["law_id"], "law", l["title"], {
        "meta": f"{l.get('category','')} · enacted {l.get('enactment_date','?')} (Knesset {l.get('knesset_number','?')})",
        "role": "",
        "events": [{"when": l.get("enactment_date",""), "what": "Summary", "text": l.get("summary","")}],
        "personal": [{"title": "Land impact", "when": "", "text": (l.get("land_impact") or {}).get("description","")}]
                    if (l.get("land_impact") or {}).get("description") else [],
    })

for t in topics:
    add_node("topic:" + t["topic_id"], "topic", t["name"], {
        "meta": f"{t.get('topic_type','')} · {t.get('date_or_range','')}", "role": "",
        "events": [{"when": t.get("date_or_range",""), "what": "Summary", "text": t.get("summary","")}],
        "personal": [{"title": "Significance", "when": "", "text": t.get("significance","")}] if t.get("significance") else [],
    })

# Present-day foreign patrons/lobbyists (schema #4) -- shares the "actor" shape treatment
# (they're people) but a dedicated kind so the info panel and index can still label them
# distinctly. Left "unaffiliated" by default: the Right/Left/Religious/Institutional spectrum
# this classifier models is Israeli domestic politics, which doesn't meaningfully apply to a
# US/Canada-based nonprofit director -- not a gap, an honest non-fit.
for f in foreign:
    add_node("foreign:" + f["actor_id"], "foreign", f["full_name"], {
        "meta": f.get("organizational_role", "") + (f" · {f['organization']}" if f.get("organization") else ""),
        "role": f.get("public_registration", ""),
        "events": [{"when": e.get("date",""), "what": e.get("action_type",""), "text": e.get("description","")}
                   for e in f.get("action_record", [])],
        "personal": [{"title": "Role status", "when": "", "text": f.get("role_status", "")}] if f.get("role_status") else [],
    })
    nodes[node_index["foreign:" + f["actor_id"]]]["align"] = "unaffiliated"

# ---------- edges ----------
edges = []
seen_edges = set()

def add_edge(a, b, kind):
    if a not in node_index or b not in node_index:
        return
    key = tuple(sorted([a, b])) + (kind,)
    if key in seen_edges:
        return
    seen_edges.add(key)
    edges.append({"source": a, "target": b, "kind": kind})

# person <-> org, from org.notable_members (structured, already-linked ids)
for o in orgs:
    oid = "org:" + o["org_id"]
    for mid in o.get("notable_members", []):
        if ("actor:" + mid) in node_index:
            add_edge(oid, "actor:" + mid, "member")
        elif ("mk:" + mid) in node_index:
            add_edge(oid, "mk:" + mid, "member")

# org <-> org, from lineage
for o in orgs:
    oid = "org:" + o["org_id"]
    lin = o.get("lineage", {}) or {}
    for pid in lin.get("predecessor_orgs", []) or []:
        if " " not in pid and "(" not in pid:
            add_edge("org:" + pid, oid, "lineage")
    for sid in lin.get("successor_orgs", []) or []:
        if " " not in sid and "(" not in sid:
            add_edge(oid, "org:" + sid, "lineage")
    mi = lin.get("merged_into")
    if mi and " " not in mi and "(" not in mi:
        add_edge(oid, "org:" + mi, "lineage")

# Standing organs of a parent body ("component of") aren't a predecessor/successor relationship
# -- the UN Charter didn't dissolve into the General Assembly and Security Council, they're
# permanent bodies within it -- so this doesn't belong in organizations.json's lineage fields,
# which mean actual succession. A small explicit list here (same spirit as MANUAL_ALIASES in
# collision_check.py: a real, uncontroversial, well-documented relationship that doesn't fit the
# general schema) instead of forcing a wrong "predecessor" claim into the org's own record.
COMPONENT_OF = {
    "united-nations-general-assembly": "united-nations",
    "united-nations-security-council": "united-nations",
}
for child, parent in COMPONENT_OF.items():
    add_edge("org:" + parent, "org:" + child, "component")

# law <-> mk/org: structured sponsoring_mk_id, PLUS names/org names already named in the law's
# own (already-vetted) summary text -- extraction, not invention.
people_names = [(("mk:" + m["mk_id"]), m["full_name"]) for m in mks] + \
               [(("actor:" + a["actor_id"]), a["full_name"]) for a in actors]
GENERIC_ORG_IDS = {"knesset", "state-of-israel"}  # too generic to be a meaningful law link
for l in laws:
    lid = "law:" + l["law_id"]
    sid = l.get("sponsoring_mk_id")
    if sid:
        add_edge(lid, "mk:" + sid, "sponsor")
    text = l.get("summary", "")
    for pid, name in people_names:
        if name in text:
            add_edge(lid, pid, "sponsor")
    for o in orgs:
        short = o["name"].split("(")[0].strip()
        if o["org_id"] not in GENERIC_ORG_IDS and len(short) > 4 and short in text:
            add_edge(lid, "org:" + o["org_id"], "sponsor")

# topic <-> actor/mk/foreign/org, straight from each topic's own related_* fields
for t in topics:
    tid = "topic:" + t["topic_id"]
    for aid in t.get("related_actor_ids", []) or []:
        add_edge(tid, "actor:" + aid, "context")
        add_edge(tid, "mk:" + aid, "context")      # harmless no-op if the actor: form already matched
        add_edge(tid, "foreign:" + aid, "context")  # ditto -- none currently match, kept for when one does
    for oid in t.get("related_org_ids", []) or []:
        add_edge(tid, "org:" + oid, "context")

# topic <-> law, matched against each law's short title appearing in the topic's own summary text
# -- e.g. Resolution 497's summary names "the Golan Heights Law" directly. Same extraction-not-
# invention discipline as the law<->org/person matching above; topics.json has no related_law_ids
# field to read from structurally, so text matching is the only way this connects at all.
for t in topics:
    tid = "topic:" + t["topic_id"]
    text = (t.get("summary", "") or "") + " " + (t.get("significance", "") or "")
    for l in laws:
        short = l["title"].split(",")[0].strip()
        if len(short) > 4 and short in text:
            add_edge(tid, "law:" + l["law_id"], "context")

# foreign <-> org, matched against each patron's own `organization` text field the same way laws
# match sponsor org names -- currently a no-op (none of the 6 foreign patrons' organizations are
# themselves in organizations.json, which tracks the Zionist-movement/Israeli-state org lineage,
# not the US/Canada-based nonprofits these patrons lead), kept so it starts working the moment
# either file grows to overlap.
for f in foreign:
    org_text = f.get("organization", "")
    for o in orgs:
        short = o["name"].split("(")[0].strip()
        if len(short) > 4 and short in org_text:
            add_edge("foreign:" + f["actor_id"], "org:" + o["org_id"], "member")

# ---------- alignment: MKs first, from their own recorded political_alignment ----------
# knesset_members.json's own knesset_terms[].political_alignment is real, curated per-term data
# (from the Knesset's own records) -- a far better source for an MK's alignment than inferring it
# through which orgs they're linked to. Use the most recent term (people's declared alignment can
# genuinely change across a long career). Falls through to org-propagation below only for MKs
# with no term data at all.
#
# "Centrist" is a real, positive classification (Nick, 2026-09-03) -- a party confirmed centrist
# is a different claim from a party we simply have no alignment data for, so it gets its own
# colour rather than folding into the same "no data" hollow-ring treatment.
#
# The Knesset's own "Religious Nationalist" label conflates two genuinely different currents:
# Religious Zionism (settlement-focused, e.g. Jewish Home/Religious Zionism party) and Haredi
# non-Zionism (UTJ, Torah-focused, historically opposed to the state's secular Zionist premise --
# already documented in this dataset's own United Torah Judaism entry). Coloring a UTJ MK the same
# "religious" as a Religious Zionism MK would erase a distinction the dataset itself draws
# elsewhere, so Haredi parties are exempted from this field override and fall through to
# org-propagation instead, which already resolves UTJ correctly.
ALIGNMENT_FIELD_MAP = {
    "Right": "right", "Far-Right": "right",
    "Left": "left",
    "Religious Nationalist": "religious",
    "Center": "centrist",
}
HAREDI_NON_ZIONIST_PARTIES = {"United Torah Judaism"}  # extend if Shas or similar is ever added
for m in mks:
    terms = m.get("knesset_terms", []) or []
    if terms:
        latest = terms[-1]
        if latest.get("party") in HAREDI_NON_ZIONIST_PARTIES:
            continue
        mapped = ALIGNMENT_FIELD_MAP.get(latest.get("political_alignment"))
        if mapped:
            nodes[node_index["mk:" + m["mk_id"]]]["align"] = mapped

# ---------- alignment propagation to remaining people, laws, and topics ----------
person_org_aligns = {}
for e in edges:
    for a, b in [(e["source"], e["target"]), (e["target"], e["source"])]:
        if a.startswith("org:") and (b.startswith("actor:") or b.startswith("mk:")):
            person_org_aligns.setdefault(b, []).append(org_alignment.get(a[4:], "institutional"))
for nid, votes in person_org_aligns.items():
    if nodes[node_index[nid]]["align"] is None:  # don't override a real political_alignment value
        nodes[node_index[nid]]["align"] = Counter(votes).most_common(1)[0][0]
for n in nodes:
    if n["kind"] in ("actor", "mk") and n["align"] is None:
        n["align"] = "unaffiliated"

for l in laws:
    lid = "law:" + l["law_id"]
    aligns = [nodes[node_index[o]]["align"] for e in edges
              for o in (e["target"] if e["source"] == lid else e["source"] if e["target"] == lid else None,)
              if o and nodes[node_index[o]]["align"]]
    nodes[node_index[lid]]["align"] = Counter(aligns).most_common(1)[0][0] if aligns else "unclassified"

for t in topics:
    tid = "topic:" + t["topic_id"]
    aligns = [nodes[node_index[o]]["align"] for e in edges
              for o in (e["target"] if e["source"] == tid else e["source"] if e["target"] == tid else None,)
              if o and nodes[node_index[o]]["align"]]
    nodes[node_index[tid]]["align"] = Counter(aligns).most_common(1)[0][0] if aligns else "unclassified"

# ---------- report ----------
print("nodes:", len(nodes), dict(Counter(n["kind"] for n in nodes)))
print("edges:", len(edges), dict(Counter(e["kind"] for e in edges)))
print("alignment:", dict(Counter(n["align"] for n in nodes)))
law_ids = {n["id"] for n in nodes if n["kind"] == "law"}
law_edges = {e["source"] if e["source"] in law_ids else e["target"]
             for e in edges if e["source"] in law_ids or e["target"] in law_ids}
print(f"laws with >=1 edge: {len(law_edges)}/{len(laws)}")
topic_ids = {n["id"] for n in nodes if n["kind"] == "topic"}
topic_edges = {e["source"] if e["source"] in topic_ids else e["target"]
               for e in edges if e["source"] in topic_ids or e["target"] in topic_ids}
print(f"topics with >=1 edge: {len(topic_edges)}/{len(topics)}")

# ---------- splice into the template ----------
graph_data_json = json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False)
template = TEMPLATE_PATH.read_text(encoding="utf-8")
if "/*__GRAPH_DATA__*/" not in template:
    raise SystemExit("Template is missing the /*__GRAPH_DATA__*/ placeholder.")
output = template.replace("/*__GRAPH_DATA__*/", graph_data_json)
OUTPUT_PATH.write_text(output, encoding="utf-8")
print(f"wrote {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size} bytes)")
