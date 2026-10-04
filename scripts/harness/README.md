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

## Engagement-layer checks (added 2026-10-04)

`wiki_harness.js` section 16 covers the reader-engagement features: the Oslo "days overdue" stamp (the
day count must equal today's, and link to the Oslo entry), Trails (list, fresh trail, opening a step files
it, the trail bar and next-step link, the Filed stamp once a trail is finished), the "Who said it?" quiz
played end to end with the correct answer each time, wrong picks, double clicks, and the best score being
remembered, and every page still rendering when browser storage is blocked. The data behind Trails and the
quiz is checked separately by `scripts/check_engagement.py` (every trail step resolves; every quotation
is verbatim in the entry it is credited to).
