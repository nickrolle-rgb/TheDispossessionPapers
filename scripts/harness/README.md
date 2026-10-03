# Verification harnesses

Node DOM-stub harnesses that load the built HTML files and exercise the wiki and the standalone
network prototype without a browser. Run everything with `python scripts/verify_all.py` from the
project root; run these two directly only when debugging.

- `wiki_harness.js` loads `wiki-prototype.html`: routing, autolinks, network view, panels, and it
  dumps the wiki's own graph edges (`js_edges.txt`, into `$SCRATCH_DIR` if set) for the edge-parity diff.
- `prototype_harness.js` loads `prototypes/network_view.html`: the same behaviours on the standalone build.

One line prints `false` by design: `intro overlay in body.children`. It is a DOM-stub artifact (the stub
does not track the overlay in `body.children`; the following "removed after dismiss" check passes). It
prints `false` on commits from many rounds back too, and `verify_all.py` whitelists it explicitly.

History: these were reconstructed on 2026-10-04 by replaying the original Write/Edit calls from the old
session transcript, after the session scratchpad that held them was reset. The reconstruction reproduces
the edge counts recorded in earlier rounds (537 and 539) when run against those commits.
