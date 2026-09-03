# Prototypes

Design/interaction experiments, not part of the live wiki. Kept here (checked into the repo,
not just an ephemeral Claude-side artifact) so a future session can pick up and iterate on the
actual source rather than reconstructing it from scratch, and so the alignment classifier's
reasoning is reviewable and version-controlled.

## Network view

`network_view.html` — the whole archive (Actors, Knesset Members, Organizations, Laws, Topics)
as one flip-able, clickable, searchable force-directed graph, built from the same `data/*.json`
files as the real wiki. Regenerate after any data change:

```bash
python prototypes/build_network_view.py
```

- `network_view_template.html` — the page shell: layout, CSS (reuses the wiki's own parchment/
  ink/rust/ochre/verdigris palette and Fraunces/Public Sans/IBM Plex Mono type system), and all
  the JS (hand-rolled force simulation, no library, matching wiki-prototype.html's own
  zero-dependency approach) — everything except the data itself.
- `build_network_view.py` — loads the live data files, derives nodes/edges from *structured*
  fields only (org membership, org lineage, law sponsorship, topic cross-references, plus a
  small explicit `COMPONENT_OF` map for standing UN organs — never free-text guessing), runs the
  political-alignment classifier, and splices the result into the template to produce
  `network_view.html`.

**The alignment classifier** (why a node is coloured Right/Left/Religious/Institutional/no-data)
is a real, if approximate, three-pass system — see the comments in `build_network_view.py` for
the full reasoning: org type decides genuine institutions first (never overridden by ideology
text — the "could change hands" test), then direct ideology-keyword match, then lineage
propagation for parties whose own ideology tag doesn't keyword-match but whose predecessor does
(this is what correctly colours Kadima via Likud without hardcoding it). Anything still
unresolved (a genuine centrist party, a non-Zionist Haredi party, an early proto-movement) is
left as honest "no data" rather than folded into "institutional" as a catch-all.

**Known gaps, not yet addressed:**
- `current_foreign_actors.json` (6 entries) isn't in the graph at all yet — only historical
  actors, MKs, orgs, laws, and topics are.
- 8 of 17 laws and 4 of 63 topics still have zero edges — genuinely thin sourcing, not a
  rendering bug (see the script's own console output for exact figures each run).
- No re-layout on zoom (a clicked node's neighbours keep their force-simulated positions rather
  than rearranging cleanly around it).

## Lineage sketches

`lineage_sketches.html` — three smaller, static (non-interactive) diagram sketches that predate
the network view: an org lineage web, a Venn-style affiliation overlap, and a flip-card demo
(text article face / diagram face) for a single entity. Superseded in spirit by the network view
for anything that needs to be interactive, kept for reference.
