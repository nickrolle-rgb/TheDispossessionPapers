# Zionism Timeline — Scope

*(renamed 2026-08-31, was "Palestinian Land Loss")*

Backend/database project. Green-field build, independent of Settlement Encroachment Map's
codebase — only *correlatory* output (i.e. a derived table of dated, geolocated events) gets
imported into that map's timeline slider later. This repo owns the historical research and
the queryable data model; it is not the map itself.

## Goal

A complete, queryable timeline of actions — land acquisition, policy lobbying, legislation,
executive action — from the pre-state period through the present, structured so it can
correlate against spatial/boundary change over time. Designed to be **expandable toward
near-live**: historical actors are a closed, finite set; Knesset legislative activity is not,
and should eventually pull from a live feed rather than manual entry.

## Locked decisions (2026-08-31)

- **Two entity types, two schemas:** `historical_actors.json` (pre-state Zionist figures,
  foreign patrons, land-trust founders) and `knesset_members.json` (MKs + the legislative
  items they acted on, including sitting/living MKs — see scope note below). Both **locked**,
  see `SCHEMA.md`.
- **Citations: best-effort, not verified.** Claude fills the citation field with its best
  knowledge but does not have live source access in this session. Nick verifies before
  anything here is treated as ground truth or exported downstream. Where confidence is low,
  the citation value itself will say so (e.g. `"UNVERIFIED — best guess: ..."`) rather than
  presenting a fabricated-but-confident-looking source.
- **Living/sitting MKs — in scope, but restricted for now.** Only public personal details
  (name, party, terms) and voting history go in without a citation attached at draft time —
  these are on-the-record facts. Anything more interpretive (`land_impact.description`,
  `estimated_hectares_affected`, characterizations of an action's effect) gets a citation
  before it's added for a living MK, or is left null/omitted rather than asserted uncited.
  Nick's instruction: "nothing defamatory, all public... anything else will be cited before
  ANY publication" — this project can hold uncited draft material privately, but nothing
  leaves this dataset for publication without a source.
- **Near-live path for the Knesset side:** Knesset Open Data (data.gov.il / Knesset XML web
  services, and the oknesset.org project built on it) publishes bill and vote records
  on an ongoing basis — this is the intended eventual collector, not manual entry, once the
  schema is validated.
- **Tone/classification discipline carried over from Money Tracker:** classify by documented
  conduct (what a law/action did, sourced), not by label or affiliation. No unsourced
  characterization of intent.

## Calibration set

Before scaling to "complete," validate the schema against a small set of actions that are
independently well-documented, to catch schema gaps and citation-discipline failures early —
same role Millpond's JMSDF/Cheonghae public-ground-truth set plays there.

Proposed (pending Nick's confirmation — see chat):
- **Historical actors:** Yehoshua Hankin, Baron Edmond de Rothschild, Arthur Ruppin, Menachem
  Ussishkin (JNF).
- **Legislative items:** Absentees' Property Law (1950), Land Acquisition (Validation of Acts
  and Compensation) Law (1953).

## Actor roster (expanded 2026-08-31)

`historical_actors.json` grown from the 4-person calibration set to 18, covering the arc Nick
asked for — concept → emigration → colonization:
- **Proto-Zionism / precursor thought:** Moses Hess, Zvi Hirsch Kalischer, Leon Pinsker
- **Political Zionism / founding institutions:** Theodor Herzl, Max Nordau, Zvi Hermann
  Schapira (proposed the JNF)
- **Cultural Zionism:** Ahad Ha'am (notably including his 1891 internal critique of settler
  treatment of the Arab population)
- **Ground-level Aliyah/colonization:** Israel Belkind (Bilu, First Aliyah), A.D. Gordon, Berl
  Katznelson (Second Aliyah/Histadrut)
- **Diplomatic patronage (Balfour era):** Chaim Weizmann, Nahum Sokolow, Arthur James Balfour
  (foreign patron)
- **Revisionist strand:** Ze'ev Jabotinsky (Iron Wall doctrine, ideological line to later
  territorial-maximalist settlement politics)

Same citation discipline as the calibration set — every citation is Claude's best-effort
knowledge, marked `UNVERIFIED`, pending Nick's review. Not yet reviewed.

Further expanded same day with 6 more actors: David Ben-Gurion and Golda Meir (pre-1948
portion only — their Knesset/premiership record belongs in `knesset_members.json` if added
later), Yosef Weitz (JNF Lands Department, 1948 Transfer Committee), Chaim Arlosoroff (Haavara
Agreement), Abba Hillel Silver (US fundraising/lobbying), William Robert Peel (Peel Commission,
1937 partition/transfer report). 24 actors total.

## Organizations — `data/organizations.json` (added 2026-08-31)

One schema covers parties, militias, and pre-Mandate groups together — see `SCHEMA.md` §3 for
the reasoning against a second membership-only file. Calibration set: 7 orgs tracing two
lineage chains — Bar-Giora/Hashomer → Haganah (mainstream), and Irgun/Lehi → Herut → Likud
(Revisionist), plus Poalei Zion → Ahdut HaAvoda → Mapai → Israeli Labor Party as one combined
entry (not yet split into per-stage records). Includes Non-Sanctioned Militant Action entries
(King David Hotel bombing, Deir Yassin, Lord Moyne and Bernadotte assassinations) with disputed
casualty figures left as ranges, not single asserted numbers, per the same discipline as
elsewhere in this dataset.

**Loose ends tidied (2026-08-31):** the 8 placeholder names in `organizations.json` (Yisrael &
Manya Shochat, Yitzhak Sadeh, Moshe Dayan, Yigal Allon, Menachem Begin, Avraham Stern, Yitzhak
Shamir) are now full `historical_actors.json` entries with real `actor_id`s, and every
`notable_members` reference resolves. 32 actors total. Note: several of these (Dayan's 1967
role, Allon Plan, Begin's and Shamir's premierships) carry key_land_actions into the post-1948/
post-1967 period since that's where their land-policy significance actually is — same
convention as Ben-Gurion/Meir.

## Current Foreign Actors — `data/current_foreign_actors.json` (added 2026-08-31)

**Explicitly independent of Money Tracker** — Nick: "I want no relation to Money Tracker...
build this independently," and separately flagged intent to eventually delete Money Tracker
entirely (not actioned; permanent deletion is something Claude won't execute even on request —
see memory). Scope locked to **institutional public role only**: org officers, registered
lobbyists, people named in press in their professional capacity. No private individuals, no
religion/ethnicity field anywhere. See `SCHEMA.md` §4 for the full schema and the `role_status`
field (`CONFIRMED`/`UNCONFIRMED`), added because "who currently holds role X" turns over faster
than this session can verify — most current officeholders are deliberately left unnamed
(`UNCONFIRMED`) rather than guessed. Calibration set: 5 entries — Nefesh B'Nefesh (US/Canada,
named director, `CONFIRMED` — long public tenure), Jewish Agency for Israel (global),
UJIA (UK), Zionist Federation of Australia, CIJA (Canada — registered federal lobbyist, the
cleanest "documented public role" example since the Registry of Lobbyists is itself the
citation). Four of five are placeholder-quality only — real per-country research still needed.

**Live research pass 2026-08-31:** verified 3 of 4 `UNCONFIRMED` orgs directly via browser,
against primary registries/the orgs' own sites, not memory:
- **Jewish Agency for Israel** — split into two person-entries per its dual-chair structure:
  Doron Almog (Chairman of the Executive, since Aug 2022) and Mark Wilf (Chairman of the Board
  of Governors, since Jul 2022), both confirmed via jewishagency.org's own leadership pages.
- **UJIA (UK)** — confirmed via the UK Charity Commission register: charity number 1060078,
  £12,531,000 income, 9 named trustees with appointment dates. No individual flagged as "Chair"
  in the register itself, so no single officer entry — stayed institutional.
- **Zionist Federation of Australia** — confirmed via ZFA's own team page and the ACNC
  register: Jeremy Leibler (President) and Alon Cassuto (CEO), ABN 62090880872, $3.6M AUD
  revenue. Split into two person-entries.
- **CIJA (Canada) — closed permanently, 2026-08-31.** Repeated automated lookup attempts
  against both lobbycanada.gc.ca (Cloudflare bot-check) and cija.ca (empty JS render, then
  unresponsive click-through) coincided with session crashes on Nick's end. **Per Nick's
  explicit instruction: no further automated fetch attempts against either domain, ever, in
  this project.** If this entry is ever needed, it gets sourced manually by Nick, not by
  Claude. Entry left `UNCONFIRMED` in the data file with this closure noted inline.

`current_foreign_actors.json` now has 7 entries (up from 5): 6 `CONFIRMED`, 1 institutional
(UJIA) with confirmed org-level facts but no named officer, 1 (CIJA) still fully `UNCONFIRMED`.

## Knesset scraper — `scripts/knesset_scraper.py` (added 2026-08-31)

Pulls directly from the Knesset's own OData services (ParliamentInfo.svc, Votes.svc), not
scraped HTML or a third party. Full findings and design reasoning are in the script's own
docstring — summary:

- **973 confirmed unique MKs** (of 1,188 total `KNS_Person` rows — the rest are non-MK
  officials), **2,982 term records**, **545 factions** — all scraped and in
  `data/knesset_votes.sqlite3`, small tables also exported to `data/knesset_roster_raw.json`.
- **Confirmed live: individual roll-call votes only exist from Knesset 16 (2003) onward.**
  `knesset_num lt 16` returns zero rows — validates the caveat already in the Kaplan/Eshkol
  calibration entries. Knessets 1-15 (1949-2003) stay manual/narrative.
- **1,275,825 per-MK vote-result rows exist** across 24,744 votes (2003-2021 confirmed so far;
  most recent header row scraped is 2021-07-13, Knesset 24 — needs checking whether
  `View_vote_rslts_hdr_Approved` actually covers 2022-present or whether that's a real gap).
- **Storage: SQLite, not flat JSON**, for the bulk vote data — 1.27M rows would be a
  ~150-200MB unopenable JSON file. This is a deliberate departure from the other three files'
  flat-JSON pattern, done with Nick's sign-off pending as of this note (see chat). Vote headers
  (24,744 rows) scraped; the 1.27M-row vote_results pull (~12,758 requests, ~2+ hours at a
  polite rate) has NOT been launched yet — awaiting explicit go-ahead.
- **No shared ID between the two OData services** — `KNS_Person.PersonID` and
  `vote_rslts_kmmbr_shadow.kmmbr_id` are different ID spaces (confirmed live: PersonID 12
  doesn't exist, but a Votes-side id 12 does). Joining a roster entry to its vote history needs
  a name-based match, not a numeric join — flagged as follow-up work in the script, not solved
  yet.
- A transform step from SQLite into the locked `knesset_members.json` schema is planned but not
  yet written.

**v3→v4 switch (2026-08-31):** the legacy v3 Votes.svc (`vote_rslts_kmmbr_shadow` /
`View_vote_rslts_hdr_Approved`) was found to be a stale, dead replication — stopped updating at
Knesset 24, mid-2021 ("shadow" in the table name was the tell). Found via web search after the
staleness looked suspicious, then verified live. Switched entirely to
`OdataV4/ParliamentInfo` (`KNS_PlenumVote`, `KNS_PlenumVoteResult`, `KNS_PlenumSession`):
current through 2026-07-28, ~1.95M vote-result rows (vs. 1.27M in the dead v3 table), and —
critically — `KNS_PlenumVoteResult.MkId` **is the same ID space as `KNS_Person.Id`**
(confirmed live: MkId 466 = KNS_Person Id 466, same name both sides), solving the person↔voter
join problem v3 had. Nick's storage sign-off (SQLite for bulk data) confirmed 2026-08-31.

**Pre-2003 vote gap — confirmed as a real, structural absence, not a script limitation.**
Checked three independent ways: (1) both v3 and v4 vote-result tables return zero rows for
`knesset_num < 16` / sessions before 2003; (2) `KNS_PlenumSession` itself *does* have full
session metadata back to Knesset 1 (1949) and even 44 pre-state "Knesset 0" sessions — so the
Knesset knows a session happened, just not how each member voted; (3) oknesset.org's own data
pipeline (independent scrape, updated as recently as March 2026) mirrors the same v3 tables —
no earlier coverage there either, confirming this isn't a gap unique to Knesset's own systems.
**The only pre-2003 path found:** `KNS_DocumentPlenumSession` has scanned Divrei HaKnesset
(Hansard-style plenary transcripts — TIF/PDF/DOC) back to Knesset 1 session 1 — confirmed a
real file exists (`1_ptm_254201.doc` etc.). But named individual votes only appear in these
transcripts when a roll-call ("קריאת שמות") was specifically used, historically the exception
(major confidence votes) not the rule — most routine votes were by show-of-hands/count only, so
OCR/parsing this corpus would mostly recover bare vote *tallies* (already in vote headers
where they exist), not new per-MK breakdowns. Concluded: not worth pursuing as an automated
project; Knessets 1-15 stay manual/narrative-level, consistent with the Kaplan/Eshkol
calibration entries.

## Preview artifacts (2026-08-31) — outside `data/`, prototype-only

Three published Artifacts demonstrating what the eventual Settlement Encroachment Map could
look like, built from data already in this project. **Deliberately kept as standalone HTML
files, not part of the map project's codebase** — same "no relation" boundary as Money Tracker.

1. `land-loss-timeline-map.html` ("Ground Given Up") — click-through timeline, hand-drawn
   schematic map. First pass, superseded in accuracy by #3.
2. `land-loss-simple.html` ("Losing Ground") — quiet poster version, no graphic detail, same
   schematic map.
3. `land-loss-scrolly.html` ("Ground Given Up", scrolly version) — phone-sized scroll-driven
   version per Nick's request. **Uses real geographic data**: Natural Earth 50m admin
   boundaries (`ne_50m_admin_0_map_subunits.geojson`, includes West Bank/Gaza as distinct
   features from Israel), simplified via Shapely, projected to SVG. Golan Heights, Sinai, and
   the South Lebanon security zone are computed geometric clips against that real coastline
   (bounding-box intersections — approximate cut lines, real outer boundary), not hand-drawn.
   Seven stages, Ottoman rule → 2000 S. Lebanon withdrawal, with a scroll-driven camera
   (`core`/`wide` presets) that zooms out at the 1967 stage to reveal Sinai. Pre-1948 stages
   (Sursock Purchase, Peel Commission) deliberately show NO shaded polygon — no reliable
   boundary data exists for them, so they're markers-only rather than fabricated precision.
   **Sync bug fixed (2026-08-31):** Nick caught the map/card mismatch directly (screenshot
   showed post-'67 shading under the 1947-49 card). Root cause was the IntersectionObserver
   rootMargin-band approach firing out of order on tall/adjacent steps. Replaced with a
   rAF-throttled scroll handler that recomputes which step's card is closest to viewport
   center on every tick — deterministic, no ambiguity. Also per Nick's round of feedback:
   intro copy replaced ("From Ottoman rule to today, a timeline of the land taken from the
   people of Palestine"); all base-map border strokes removed (modern country lines were
   anachronistic under Ottoman framing — only active region overlays get a stroke now); all
   per-card `.note` disclaimers removed; "STAGE XX/YY" text label removed, replaced with a
   dot-progress row floating directly on the map; added a new minor "1918-1920: The Mandate
   begins" transition beat (Ottoman collapse → British Mandate) between Ottoman Rule and
   Sursock; demoted Peel Commission and Sinai-Returned from full stages to lightweight
   `type:"transition"` cards (dashed border, no stat, no map-shading change) to match —
   8 steps total now, mix of full stages and transitions.

## Wiki click-through prototype (2026-08-31)

Nick asked how hard a Wikipedia-style hyperlinked site over this data would be. Built
`wiki-prototype.html` (published as Artifact "Ground Truth") to answer concretely rather than
just estimate — embeds `historical_actors.json` + `organizations.json` (+ the small
`knesset_members.json`/`current_foreign_actors.json` files) inline, hash-routed
(`#/actor/<id>`, `#/org/<id>`), auto-links known entity names inside free-text prose (not just
structured fields) via a longest-match-first regex over full names, birth names, and *unique*
surnames (skips ambiguous ones — the two Shochats share a surname, so "Shochat" alone is never
auto-linked). Word-boundary matching added after catching a real false-positive risk
("Peel" would otherwise match inside "repeal"/"appeal").

**Added Ariel Sharon** as a real `historical_actors.json` entry to make the demo concrete (Nick's
example) — ties together Begin-era settlement expansion (Agriculture Minister 1977-81), the
1982 Lebanon invasion (already in the scrolly map's South Lebanon Zone stage), and the 2005
Gaza disengagement (already surfaced by `find_land_votes.py`'s search results). Added a
**Kadima** org entry too (Sharon's 2005 split from Likud) — 33 actors, 8 orgs total now.

**Verification note:** the local-file preview sandbox cannot execute real hash-based navigation
(confirmed: it renders as a non-live snapshot, clicks don't fire). Verified the linking logic
correctness a different way — mirrored the exact JS matching logic in Python against the real
data and confirmed it (a) correctly links surname-only mentions like "under Begin", (b) does
NOT false-positive match "Peel" inside "repeal"/"appeal" once word boundaries were added,
(c) correctly resolves Sharon's Likud/Kadima affiliations. Not the same as a live click-test —
worth Nick confirming interactively.

**Assessment for scaling this to the full dataset later:** the curated layer (actors + orgs +
a curated set of significant votes, likely low hundreds of entities) stays easily artifact-sized
this way. The full raw Knesset corpus (973 MKs, ~2M vote rows) is a different scale of problem —
would need real hosting/a static site generator, not a single embedded-JSON HTML file. Not
harder in principle, just a distinct build.

## Org pages deepened + IDF added (2026-08-31)

Nick: "party pages are slim... key actions are lean... would love party charters, a page for
the IDF." Added real content, not just more entries for volume's sake:

- **Herut** — actual 1948 founding platform content (explicit "both banks of the Jordan"
  territorial claim, rejecting the 1947 partition), plus the 1952 reparations-agreement
  protests (Begin suspended from Knesset, violence at the Knesset building itself).
- **Likud** — the 1977 "Mahapach" (first non-Labor government, directly enabling the
  settlement acceleration already in ariel-sharon's/menachem-begin's actor entries) and the
  real tension of Camp David/Sinai's full return under the same "Greater Israel" party.
- **Poalei Zion → Labor lineage** — Ber Borochov's actual 1906 ideological synthesis
  (Marxism + Zionism), the 1968 merger that formed the *current* Labor Party (previously this
  chain only went up to Mapai's 1930 founding — a real gap), and the matching 1977 election
  loss.
- **Haganah** — the Saison (1944-45, Haganah suppressing the Irgun — one Zionist militia
  acting against another) and its 1948 dissolution into the IDF.
- **Irgun** — the Altalena Affair (June 1948), a major gap: Ben-Gurion's government shelling
  an Irgun arms ship, forcing Irgun's dissolution into the IDF.
- **Lehi** — the 1948 outlawing after the Bernadotte assassination and members' path into
  mainstream politics (Shamir).
- **Kadima** — the 2006 election win under Olmert before its decline.
- **New: `idf` org entry**, `org_type: "National Military"` (new type, see SCHEMA.md) —
  founding (1948-05-26), and execution-level entries for 1967, 1982 Lebanon, and the 2005
  Gaza disengagement (notable as the one entry where the IDF's land action targeted Jewish
  settlers, not Palestinians — a real contrast worth keeping, not smoothing over). Haganah's
  `successor_orgs` now points to the real `idf` org_id instead of a placeholder string.

9 orgs, 31 action_record entries total (up from 8/15). Same UNVERIFIED-citation discipline
throughout — this is more coverage, not more certainty; still needs Nick's review before
anything here is treated as settled. `wiki-prototype.html` re-embedded with the fresh data and
republished to the same Artifact URL.

## Renamed "The Dispossession Papers" + wiki restructure (2026-09-01)

Renamed from "Ground Truth." Considered literal "wanted criminals" framing first (Nick's
original idea) and pushed back — flagged that blanket-labeling every entry "criminal" would
break the documented-conduct discipline this project has held throughout (a legal land
purchase under Ottoman/Mandate law and the Kahan Commission's finding on Sabra/Shatila aren't
the same kind of thing). Nick's response, and worth remembering for future framing calls: the
*aggregate century-long pattern* of land taken and peace undermined isn't ambiguous and doesn't
need hedging — that's a different claim than asserting individual criminality on every profiled
person, and "dispossession" (standard historiographical term, not euphemism) names the pattern
forthrightly without that overreach. Landed on "The Dispossession Papers" — deliberately evokes
Pentagon/Panama Papers, reads as exposed documents.

Also: (1) split the combined `poalei-zion-to-labor` entry into four real, separately-linkable
pages (`poalei-zion`, `ahdut-haavoda`, `mapai`, `israeli-labor-party`), chained via `lineage`
— direct response to Nick asking "do we have a page for Mapai" (no, this is why); (2) added
`south-lebanon-army` org entry, which also fixed a dangling reference (idf's action_record
claimed a "south_lebanon org entry" that never actually existed as a real org — now it does);
(3) stripped every `.json`/internal-slug mention from reader-facing text across all four data
files — those were always meant as Claude's own working notes, not prose; (4) improved the
wiki's auto-linker: extended surname-matching to MK entities (not just actors), and added
short-name aliasing for orgs whose formal `name` carries a parenthetical subtitle ("Herut
(Freedom Movement)" -> also matches bare "Herut"; "IDF" and "Irgun" added as manual aliases
since the generic split-on-`(`/`/` heuristic didn't produce them). 13 orgs now, 33 actors.
Republished to the same Artifact URL, favicon changed to 🗂️ (deliberate — new name, new mark).

## "Encyclopedia, not a database skin" pass (2026-09-01)

Nick: "I would like this to read as an encyclopedia of peoples, parties and events, not as a
skin over a broader database which it clearly is." Two things:

1. **Screenshot 1 he flagged was a stale/cached view** — the exact sentence he screenshotted
   ("This single lineage chain is recorded as one entry rather than four separate org records
   — split into separate `org_id`s later if...") was already gone from the data before he sent
   it; confirmed via grep (0 matches). Not a bug to fix, just a client-side cache — worth
   remembering that "did this actually make it live" is sometimes worth a quick data-side check
   before assuming a report is describing current state.
2. **Real cleanup needed and done**: swept all four files for "process voice" — meta-commentary
   about the project/pipeline itself, distinct from the citation-confidence UNVERIFIED notes
   (which stay, Nick wants those). Fixed phrases like "before publication," "not confirmed by
   Claude," "this research pass," "Nick asked," "pull dated examples... before using in the
   timeline." `current_foreign_actors.json` was the worst offender (rewrote all 6 entries) —
   also **dropped the CIJA stub entirely** rather than leaving an empty article explaining a
   failed lookup; the "don't retry" instruction lives only in this doc and memory now, not in
   reader-facing data. One regex replacement left a grammar artifact ("Verify Kaplan's ... is
   not independently corroborated here") — caught and fixed on the next pass; worth
   double-checking output text after any bulk find-replace, not just JSON validity.

On the "keep the 4 party pages split or merge them" question Nick left open ("I really don't
mind"): recommended keeping them split — matches the encyclopedia framing better (Wikipedia
gives Mapai, Ahdut HaAvoda, and Israeli Labor their own articles too, despite the direct
lineage), and it's already built this way.

## Institutional layer added: Hapoel Hatzair, Yishuv, State of Israel (2026-09-01)

Nick asked for Yishuv and "Israeli State" entries; also caught a real gap myself while doing
it — Mapai's own founding text names Hapoel Hatzair as a co-merger partner alongside Ahdut
HaAvoda, but only Ahdut HaAvoda had gotten a page. Fixed:

- **Hapoel Hatzair** (1905-1930) — A.D. Gordon's non-Marxist "religion of labor" home,
  deliberately distinct from Poalei Zion's Marxist line. Mapai's `predecessor_orgs` corrected
  to list both co-founders.
- **Yishuv** (org_type: "Self-Governing Community", new type) — the Mandate-era Jewish
  community's actual self-governing institutions (Asefat HaNivcharim / Va'ad Leumi, est. 1920),
  not just an informal demographic term. Direct institutional predecessor of the State.
- **State of Israel** (org_type: "Sovereign State", new type) — anchors the 14 May 1948
  Declaration of Independence at the state level without duplicating the land-law detail
  already carried in Kaplan's/Eshkol's/Ben-Gurion's own entries; description explicitly notes
  that later legislative action flows through Knesset/IDF as organs of this state.

**Caught and fixed before publishing:** named the org "The Yishuv" but had written "the
Yishuv" (lowercase article) everywhere in prose — the linker is case-sensitive, so "The" vs
"the" would have silently failed to match. Renamed to just "Yishuv" (also matches how
Wikipedia titles its own article on the subject). Verified the fix via the same Python-mirror
technique used throughout this project before republishing, not just eyeballing it.

16 orgs total now.

## New entity kind: Laws, plus Knesset org, plus MK pages actually work now (2026-09-01)

Nick asked for a Knesset page and pages for specific laws (Absentees' Property Law, Land
Acquisition Law). Building this exposed a real functional gap: **MK pages (Kaplan, Eshkol)
were in the data but never actually rendered** — the wiki only had `renderActor`/`renderOrg`;
anything else silently fell through to "Page type not yet implemented." Fixed properly, not
just added laws on top of a broken foundation:

- **New `data/laws.json`** (5th data file) — `law_id`, title/Hebrew title, official Sefer
  HaChukim citation, enactment date, sponsoring ministry + `sponsoring_mk_id` (links to the
  actual minister), category, summary, `land_impact`. Two entries: Absentees' Property Law
  (1950), Land Acquisition Law (1953) — content adapted from what already lived inside
  Kaplan's/Eshkol's `knesset_members.json` entries, now given their own proper pages instead.
- **New `renderMK()`** — Knesset Member pages now actually render (they never did before).
- **New `renderLaw()`** — full law pages: infobox (enacted date, sponsoring ministry/minister,
  official citation), summary, land impact section.
- **`personLink()` replaces `actorLink()`** — the old helper only checked `historical_actors.json`
  IDs; a law's `sponsoring_mk_id` or an org's `notable_members` entry pointing at an MK would
  have silently shown "(not yet profiled)" even though the person's page existed. Now checks
  both `actor:` and `mk:` prefixes.
- **New `Knesset` org entry** (org_type: "Legislative Body", new type) — First Knesset convened
  14 Feb 1949, direct successor to the Yishuv's Asefat HaNivcharim; notes both 1950s land laws
  were passed in its first two sessions.
- **Caught before publishing:** the law title "Land Acquisition (Validation of Acts and
  Compensation) Law, 5713-1953" doesn't reduce to "Land Acquisition Law" via the existing
  comma-split short-alias heuristic (the parenthetical sits in the middle, not just a trailing
  date) — added as a manual alias after the Python-mirror verification caught the miss.

17 orgs, 2 laws, 2 MKs (now actually reachable) — index page updated with Laws and Knesset
Members sections.

## New entity kind: Topics — the long tail (places, periods, events, publications) (2026-09-01)

Nick's batch request (Ber Borochov, Aliyah waves, Jezreel Valley, Sursock family, PLDC, JNF,
WZO, 'Auto-Emancipation', Hovevei Zion, Kattowitz Conference, First Zionist Congress, Haavara
Agreement, Jewish Agency for Palestine) sorted cleanly into three buckets:

1. **One real person** (Ber Borochov) → `historical_actors.json`, 34th entry. Also fixed
   Poalei Zion's `notable_members` to actually list him (he was only referenced in prose
   there before, not as a real linked actor).
2. **Five real organizations** (World Zionist Organization, Jewish National Fund, Palestine
   Land Development Company, Hovevei Zion, Jewish Agency for Palestine) → `organizations.json`,
   fit the existing schema fine. **Jewish Agency for Palestine (1929, pre-state) is distinct
   from "Jewish Agency for Israel" in current_foreign_actors.json (post-1948)** — noted the
   succession explicitly in its action_record rather than conflating them.
3. **Everything else** (Jezreel Valley, Sursock family, the 5 Aliyah waves, 'Auto-Emancipation',
   Kattowitz Conference, First Zionist Congress, Haavara Agreement) didn't fit person/org/law —
   built a 6th data file, **`data/topics.json`**, one flexible schema covering Geographic
   Region / Migration Period / Historical Event / Publication / Agreement / Family-Lineage,
   same principle as Wikipedia varying its infobox by context rather than needing structurally
   different article types. New `renderTopic()`, wired into `route()` and the index. Schema
   documented retroactively in SCHEMA.md §6 (and finally documented Laws too, §5 — that one
   was never written up when laws.json was built last round).

**Caught before publishing:** named the Auto-Emancipation topic `"'Auto-Emancipation'"` with
literal quote marks baked into the `name` field — would have required prose to type the exact
quote characters to match. Fixed to a bare `Auto-Emancipation` before embedding (same class of
mistake as the earlier "The Yishuv" vs "Yishuv" case — check how a name will actually appear in
running prose before locking it in, not just how it looks as a title).

22 orgs, 34 actors, 11 topics now. Full collision check run before publishing (Python-mirrored
linker logic against the live data) — zero name collisions across the entire dataset.

## Batch 3: Bilu, Histadrut, Asefat HaNivcharim, Va'ad Leumi + 9 topics (2026-09-01)

Nick's batch sorted into 4 new orgs and 9 new topics:
- **Orgs**: Bilu movement, Histadrut, Asefat HaNivcharim, Va'ad Leumi (org_types: Settlement
  Movement, Labor Federation, Representative Assembly, Executive Council — all new). Adding
  Asefat HaNivcharim/Va'ad Leumi let the lineage chain get more precise: Knesset's
  `predecessor_orgs` now points to `asefat-hanivcharim` specifically (not the broad `yishuv`
  umbrella), and State of Israel's now points to `vaad-leumi` — the actual assembly→parliament
  and executive-council→government threads, rather than one vague "came from the Yishuv" link.
- **Topics**: Ottoman Palestine, British Mandate, Mandatory Palestine (kept as three distinct
  entries — era/legal-regime/territory are genuinely different framings, not the same fact
  three times), kibbutz, moshavot (Institution Type), Rishon LeZion, Zichron Ya'akov
  (Geographic Region), Pogroms (Historical Phenomenon — recurring, not single-event), Balfour
  Declaration (Historical Event).

Full validation + collision check run before publishing (standing practice now) — zero issues.
26 orgs, 34 actors, 20 topics, 2 laws.

## First real citation-verification pass (2026-09-01)

Nick asked if now was a good time to start verifying UNVERIFIED citations. Scoped it rather
than attempt all ~100+ scattered citations in one pass — started with the two highest-stakes,
most checkable ones: the Sefer HaChukim references for the two laws. **Both were wrong.**
Original guesses were "vol. 4, p. 68" and "vol. 5, p. 155" — Sefer HaChukim doesn't use
volumes, it uses sequential issue numbers. Real citations, found via live web search and
cross-confirmed against a peer-reviewed source (Amnon Kedar, 'Dignity Takings and Dispossession
in Israel', 2016, JSTOR, cited 21 times):
- Absentees' Property Law → **Sefer Ha-Chukim No. 37, p. 86** (20 March 1950)
- Land Acquisition Law → **Sefer Ha-Chukim No. 122, p. 58** (20 March 1953) — page number
  single-sourced, marginally less certain than the issue number/date

Both `laws.json` entries updated with `VERIFIED 2026-09-01` citations naming exactly what was
cross-checked against what, superseding the old UNVERIFIED guesses rather than just deleting
them. **This is a real, useful finding, not a formality** — it means the "best guess" citation
discipline used throughout this project was right to hedge; a plausible-sounding guess
(vol./page format matches how legal citations often look) was still simply wrong.

**Scoping note for continuing this work:** verifying by hand this way (search, cross-check,
rewrite) took real effort for just 2 citations out of ~100+ across the dataset. Worth deciding
with Nick whether to keep going citation-by-citation, or prioritize by stakes (specific
checkable facts — dates, page numbers, casualty figures — over general "this book probably
discusses this" attributions, which are lower-value to verify precisely).

## Casualty-figure verification pass (2026-09-01)

Checked all 5 casualty figures in `organizations.json` against live sources:

- **King David Hotel bombing** — confirmed accurate (91 killed: 28 British, 41 Arab, 17
  Jewish + others; ~45 injured). Added the breakdown and the Irgun-vs-official 91/92 nuance.
- **Deir Yassin** — confirmed accurate. The 254→~110-120 revision and the range itself are
  correct; strengthened with an independent corroborating data point (Aref al-Aref's
  contemporary Palestinian count of 117, converging with the Birzeit figure from a different
  source base).
- **Altalena Affair** — was a vague "16-19" range; now precise: **19 total (16 Irgun + 3
  IDF)**, sourced to Wikipedia's infobox. Not a correction, but an upgrade from hedged range to
  confirmed breakdown.
- **Lord Moyne assassination** — **found a real gap, not just an uncertain figure**: the
  entry only named Moyne as a victim. His driver, Lance Corporal Arthur Fuller, was also killed
  intervening — corroborated by contemporary UK Parliament Hansard records. Added.
- **Bernadotte assassination** — checked for the same class of gap (a missing victim) as
  Moyne. Confirmed already complete: two deaths total (Bernadotte + André Serot), no others.

Net result: 1 real omission fixed (Moyne), 1 range tightened to a sourced breakdown (Altalena),
2 confirmed accurate as-is (King David Hotel, Deir Yassin), 1 confirmed complete (Bernadotte).
All five citations now marked `VERIFIED 2026-09-01` with what was actually checked against what.

**Still outstanding, not yet checked:** the "~750,000 Palestinians fled or were expelled"
Nakba figure lives in `land-loss-scrolly.html`'s own embedded stage text, not in the JSON data
files — a different location, easy to forget when sweeping `data/*.json`. Worth checking next
if continuing this work, along with the dunam/hectare figures still left `null` throughout
(Sursock Purchase, Absentees' Property/Land Acquisition Laws) — those were deliberately left
unasserted rather than guessed, so verifying them would mean finding a real figure to add, not
just checking an existing one.

## Standalone event/reference pages + verification round 2 (2026-09-01)

Nick had to hunt through Irgun's org page to find the Altalena Affair — real UX gap: major
events only existed as `action_record` sub-entries, not directly reachable/searchable pages.
Added 5 new topics (**The Altalena Affair, Iron Wall doctrine, King David Hotel bombing, Deir
Yassin, Dunam**) and 1 new org (**Custodian of Absentee Property**, org_type "Government
Office", new type). Fuller institutional narrative stays on Irgun's/Lehi's own pages too — these
are the directly-linkable versions, not a replacement. The new **Dunam** page carries a real
interpretive flag: the metric 1,000m² standardization happened in 1928, *after* the 1921-25
Sursock Purchase, so those dunam figures may be in the older ~900-920m² Ottoman dunam — noted
on the page rather than silently assumed away.

**Verification round 2** — 3 more checked, continuing from the casualty-figure pass:
- **Tower and Stockade settlement count** — confirmed the "50-57" hedge was well-calibrated;
  actual source variance is 52/53/57, all within the existing range. Tightened wording,
  marked VERIFIED.
- **Golda Meir's 1948 fundraising total** — was hedged as "sources vary on the exact total";
  turns out $50M (against a $25M goal) is *strongly* and consistently corroborated, including
  Ben-Gurion's own famous quote crediting her by name. Upgraded from hedged to confirmed.
  (Also fixed an unrelated typo — "commcommonly" — found while re-reading this entry.)
- **Nakba refugee figure ("~750,000")** — confirmed accurate against the documented
  700,000-800,000 range (UN's own 1950 estimate: 711,000; 1961 estimate: 800,000-900,000).
  This figure lives in `land-loss-scrolly.html`/`land-loss-timeline-map.html`, not the wiki's
  JSON data — already phrased as "roughly," no text change needed, just confirmed.

Full collision check run before publishing (standing practice). 27 orgs, 34 actors, 25 topics.

**Still outstanding for future verification rounds:** the dunam/hectare totals left `null`
throughout (Sursock Purchase, both 1950s laws) — a "find a number" task, not a "check a number"
task, different in kind from what's been done so far.

## International bodies + two wars + Nakba, verification round 3 (2026-09-01)

Added 3 orgs (**League of Nations, United Nations, United Nations General Assembly** — new
`org_type: "International Body"`) and 3 topics (**1948 Arab–Israeli War, Six-Day War, Nakba** —
new `topic_type: "Armed Conflict"`). Note on modeling: UNGA's `lineage` fields are empty rather
than pointing to `united-nations` — it's a standing organ of the UN, not something that
preceded or succeeded it, so forcing it into the succession-chain fields would misrepresent the
relationship; the connection is made in prose instead, which auto-links normally.

Nakba is kept deliberately distinct from the 1948 War topic — the war is the military campaign,
the Nakba is the displacement and its consequences (refugee status, property loss, the
Absentees' Property Law's permanent legal form). Overlapping but not the same thing; conflating
them would have been the easier, less accurate choice.

**Verification round 3** — checked every date range asserted in this batch rather than trusting
memory, since specific dates are exactly the kind of fact worth confirming:
- **1948 War end date** (20 July 1949) — confirmed against the full armistice sequence: Egypt
  24 Feb, Lebanon 23 Mar, Jordan 3 Apr, Syria 20 Jul 1949.
- **Six-Day War dates** (5-10 June 1967) — confirmed, exactly as written.
- **League of Nations Mandate for Palestine** — confirmed 24 July 1922, but found and added a
  real nuance: it didn't become legally operational until 29 September 1923, over a year later.
  Not a correction, an enrichment — the entry was accurate but incomplete.

Full collision check run before publishing. 30 orgs, 34 actors, 28 topics.

## UN Resolutions + Arab Revolt/White Paper/Armistice Line (2026-09-01)

Added 1 org (**United Nations Security Council**, `org_type: "International Body"`, parallel
to the UNGA entry) and 11 topics: 8 UN Resolutions (**181, 194, 273, 303, 242, 338, 3379, 465** —
new `topic_type: "UN Resolution"`) plus **Arab Revolt** (`Armed Conflict`), **1939 White Paper**
(`Historical Event`), and **1949 Armistice Line** (`Geographic Region`).

**New schema field: `aliases`** on topics (documented in SCHEMA.md §6). Resolution 181 and "the
1947 UN Partition Plan" are the same event, and "1947 UN Partition Plan" was already used
unlinked in several existing entries' prose (fifth-aliyah, mandatory-palestine, herut,
1948-arab-israeli-war). Rather than duplicate the topic under two ids, gave `resolution-181` an
`aliases` array (`1947 UN Partition Plan`, `UN Partition Plan`, `Partition Plan`) and wired it
into three places in `wiki-prototype.html`: the `nameIndex`-building loop (so aliases auto-link
same as the primary name), `renderTopic()` (an "Also known as" line, Wikipedia-style), and
`renderSearch()` (so searching an alias finds the page). Used the same mechanism for the
Armistice Line (`Green Line`) and White Paper (`MacDonald White Paper`) entries.

Which UN body adopted which resolution is tracked through `related_org_ids` rather than a new
field — General Assembly resolutions (181, 194, 273, 303, 3379) point to
`united-nations-general-assembly`; Security Council resolutions (242, 338, 465) point to the new
`united-nations-security-council`. Mirrored each resolution into its adopting org's own
`action_record` too (matching the existing UNGA/Resolution 181 pattern), so the org's page and
the resolution's own page tell the same story from two angles.

**"Failed attempts" (explicitly requested):** Resolution 303 (Jerusalem corpus separatum —
never implemented, both Israel and Jordan/later Israel alone kept administrative control of
their respective halves) and Resolution 3379 ("Zionism is racism" — not unimplemented but
actively revoked, by Resolution 46/86 in 1991) are flagged in their own `significance` text as
two different flavors of "failed": one dormant, one reversed.

**Verification round 4** — every date and figure in this batch checked via live search before
writing, not guessed then checked after:
- Resolutions 194, 303, 242, 338, 3379, 465, 273 — adoption dates (and 3379's 1991 revocation
  date) confirmed via live search; 242's and 465's "unanimous" passage and 465's later US
  "vote cast in error" clarification also confirmed.
- **1939 White Paper issuance date** — genuine source variance (17 vs 21 May 1939) found and
  left as a range rather than resolved to a false-precision single day; the 23 May House of
  Commons approval date is solid across sources. Same discipline as the Tower and Stockade
  and Deir Yassin entries' disputed-figure handling.
- **Arab Revolt dates** — 15 April 1936 Tulkarm killings and 19 April 1936 general-strike start
  confirmed; total casualty/troop-deployment figures not independently verified this pass
  (flagged in the citation rather than asserted).
- **1949 Armistice Line ~78% figure and "Green Line" naming** — the territorial percentage
  already existed, independently corroborated, in the 1948 Arab–Israeli War topic; only the
  Green Line naming/map-color origin itself was newly checked this pass.

Full collision check run before publishing (name collisions, dangling references, duplicate
ids — all clean). 31 orgs, 34 actors, 39 topics.

**Same-round follow-up: closed the long-outstanding dunam/hectare `null` item for both laws.**
Land Acquisition Law (1953): Adalah's own legal analysis gives **1.2-1.3 million dunams**
(~120,000-130,000 hectares) expropriated, covering the 14 May 1948-1 April 1952 window the law
retroactively validated — kept as Adalah's own range rather than picked down to a single number.
Absentees' Property Law (1950): found a real, narrower, well-sourced figure —
**over 1,000,000 dunams** specifically belonging to "present absentees" (Arab citizens who
stayed in Israel but were classified absentee for particular parcels) — but the law's *full*
administered scope also covers external refugees' land, and no single defensible total spanning
both categories exists across sources, so `estimated_hectares_affected` stays `null` with the
distinction spelled out in `description` rather than conflating a narrower confirmed figure with
the law's full, still-genuinely-uncertain scope.

## Golda Meir premiership + institutional offices + Jewish Colonial Trust + Muscular Judaism (2026-09-01)

Nick asked whether Golda Meir's entry would fill in once the Knesset scrape finishes — **no**:
the scraper populates `knesset_votes.sqlite3` vote-result rows for MKs modeled in
`knesset_members.json`, a different pipeline entirely; Meir lives in `historical_actors.json`
and isn't touched by it. Answered by expanding her entry by hand instead: her
`historical_role` now covers the Foreign Minister (1956-66) and Prime Minister (1969-74) years
that the old text explicitly deferred, and 3 new `key_land_actions` cover the 15 June 1969
Sunday Times "no such thing as Palestinians" interview, her premiership's continued West
Bank/Gaza/Golan/Sinai settlement under the Allon Plan's siting logic, and her 10-11 April 1974
resignation following the Agranat Commission's Yom Kippur War report (which cleared her of
direct responsibility, but public pressure forced the resignation anyway). Added "Israeli Labor
Party" and "Prime Minister of Israel" to her `primary_affiliations`.

Added the 4 entries Nick asked for:
- **Jewish Colonial Trust** (org, new `org_type: "Financial Institution"`) — the WZO's own
  chartered bank (London, 20 March 1899), whose Anglo-Palestine Bank subsidiary (1902, first
  Jaffa branch 1903) directly financed land purchases and ran settler credit unions. Distinct
  type from JNF's "Land Fund" — this held/lent capital, not land.
- **Prime Minister of Israel** and **President of Israel** (both orgs, `org_type: "Government
  Office"`, same type as the existing Custodian of Absentee Property) — modeled as standing
  institutional offices, `notable_members` referencing the PMs/President already profiled
  elsewhere in the dataset (Ben-Gurion, Eshkol, Meir, Begin, Shamir, Sharon; Weizmann). PM
  office's `action_record` includes a real land-relevant claim: cabinet decisions taken through
  this office, not direct Knesset legislation, have set West Bank/Gaza/Golan settlement policy
  since 1967. President's is mostly ceremonial for this dataset's purposes — flagged as such —
  with one concrete land-relevant fact kept: Knesset-passed land legislation needs the
  President's signature to take force.
- **Muscular Judaism** (topic, `topic_type: "Publication"`, same category as Iron Wall doctrine)
  — Max Nordau's 28 August 1898 Second Zionist Congress speech, the cultural-physical
  counterpart to Herzl's diplomacy; traced to the 1903 Union of Jewish Gymnastic Clubs/Maccabi
  lineage. `aliases: ["Muskeljudentum"]` used for the German term.

Full collision + dangling-reference + notable_members-reference check clean. 34 orgs, 34 actors,
40 topics.

## Verification round 5 — first pass on historical_actors.json (2026-09-01)

`historical_actors.json` had the largest unverified surface in the project (42 UNVERIFIED vs.
3 VERIFIED `key_land_actions` citations) and had never had a dedicated round — picked 5
high-value, checkable claims:

- **Yosef Weitz's Transfer Committee** — composition (Weitz, Ezra Danin, Eliahu Sasson) and the
  5 June 1948 date were both already correct; enriched with the committee's May 1948 formation,
  each member's actual institutional role, and the blueprint's real title ('Scheme for the
  Solution of the Arab Problem in the State of Israel') presented to Ben-Gurion. Softened
  "chaired" to "co-founded" — sources support membership, not a chair role specifically.
- **Peel Commission Report** — 7 July 1937 date confirmed exactly as written; enriched with the
  ~17% Jewish-state territorial figure (coastal strip, Jezreel Valley, Galilee).
- **Yigal Allon Plan — a real date correction, not just a confirmation.** Entry had guessed
  "1 July 1967"; actual cabinet presentation date is **26 July 1967** ("barely six weeks after
  the ceasefire" — corroborates the new date, not the old one). Fixed.
- **Yitzhak Shamir's 1991-92 loan guarantee dispute** — the $10 billion figure and
  settlement-freeze linkage were right; added the resolution (never granted to Shamir; approved
  for Rabin in August 1992 after Shamir's June 1992 election defeat).
- **Ariel Sharon's 2005 Gaza disengagement** — the "21 Gaza / 4 West Bank" settlement counts
  were already exactly right; enriched with the four settlements' actual names (Homesh, Sa-Nur,
  Ganim, Kadim), the 8,000+ settlers displaced, and the 12 September 2005 completion date. Same
  enrichment mirrored into the IDF org's own `action_record` entry for the same event, so both
  pages tell a consistent, equally-detailed story.

Full collision + dangling-reference check clean. Historical actors file now has 8 VERIFIED
citations (up from 3); still the largest remaining unverified surface at 37 UNVERIFIED — future
rounds should keep working through it rather than treating this as done.

## Palmach, Allon Plan, East Jerusalem, Yom Kippur War + real search/browse fixes (2026-09-01)

Nick said he'd struggled to find Bilu despite thinking it existed — it did (`bilu-movement` org,
added weeks ago), but two real, independent UX bugs explain why:

1. **Index lists were never alphabetized** — they rendered in JSON insertion order, so scanning
   the Organizations list by eye for "Bilu" meant scanning an effectively random order. Fixed:
   `renderIndex()` now sorts every category list (actors/orgs/MKs/laws/topics) alphabetically at
   render time via a sorted copy (`.slice().sort()`), never mutating the underlying arrays other
   code relies on.
2. **A real autolink gap, caught by grep, not by luck:** several entries reference bare "Bilu"
   in prose (Israel Belkind's own `primary_affiliations` literally said "Bilu (co-founder)"),
   but the nameIndex only ever had the full org name "Bilu movement" — no short form derives
   automatically since the name has no `/` or `(` to split on (the existing short-alias
   heuristic's trigger). Fixed via `MANUAL_ALIASES` (`"Bilu": "org:bilu-movement"`, same pattern
   as the earlier IDF/Irgun/Land Acquisition Law cases) and by correcting Belkind's affiliation
   text itself to "Bilu movement (co-founder)" so `linkIfKnownOrg`'s exact-substring check
   matches too.

**Nick also asked for search to cover "titles obviously, but aliases & mentions too."** It
already covered titles+aliases (added last round); mentions did not exist. Implemented properly:
every entity now gets a `searchBlob` — its entire underlying JSON record, lowercased — computed
once at load. `renderSearch()` filters against that blob (so a search hit can be a person or
place merely *mentioned* inside another entity's prose, not just its own title/alias) and ranks
results: title match first, alias match second, mention-only third (labeled "(mentioned)" in the
UI so it's clear why a result surfaced).

**New content:** 4 entries requested — **Palmach** (org, `Paramilitary/Militia`, founded May
1941 under Yitzhak Sadeh with Yigal Allon, dissolved into the IDF May 1948, 3 of the Haganah's
12 brigades in 1948); **Allon Plan** (topic, promoted from a line inside Yigal Allon's own
actor page to a standalone page — same already-verified 26 July 1967 facts from last round's
correction); **East Jerusalem** (topic, captured 7 June 1967, unilaterally annexed via municipal
boundary expansion 27-28 June 1967 and the 1980 Jerusalem Law); **Yom Kippur War** (topic, 6-25
October 1973, Sharon's Suez Canal crossing, Meir's resignation aftermath already covered on her
own page). **Bonus addition, not explicitly requested but directly on-topic:** Resolution 478
(UNSC, 20 August 1980, declared the Jerusalem Law "null and void") — found while verifying East
Jerusalem's annexation history and added since it's exactly the kind of "failed
attempt"/land-recognition resolution the earlier UN Resolutions batch was scoped to cover.

Full collision + dangling-reference check clean. 35 orgs, 34 actors, 44 topics.

## Verification round 6 (2026-09-01) — found a real error, not just gaps

Citation review requested by Nick (counts below). Picked 4 more historical_actors.json claims:

- **Herzl's El-Arish/Uganda Scheme** — enriched: El-Arish (1902) was rejected because the
  territory was inhabited and not fully under British control; the "Uganda Scheme" (1903) was
  actually the Guas Ngishu plateau near Nairobi, popularly but inaccurately remembered as
  "Uganda"; debated at the Sixth Zionist Congress in August 1903 specifically. VERIFIED.
- **Jabotinsky's Revisionist Zionist Organization** — tightened from bare "1925" to the actual
  25 April 1925 Paris founding date, and its real name (Revisionist Zionist Alliance / World
  Union of Zionist Revisionists). VERIFIED.
- **Avraham Stern's Nazi contacts** — the existing hedge ("exploring controversially wartime
  contact with Axis representatives") was already directionally right; filled in with the actual
  December 1940 proposal (aid to German Middle East conquest for recognition of a Jewish state,
  a scheme to recruit a European Jewish army), sourced to April 2026 Israeli-archive
  declassifications reported by Haaretz and others. VERIFIED.
- **Chaim Arlosoroff's Haavara Agreement role — a real error, not just a gap.** This entry (and
  the matching `topics.json` Haavara Agreement entry) dated his role to the 25 August 1933
  signing itself. He was assassinated on a Tel Aviv beach on **16 June 1933** — over two months
  *before* that date. He conducted the founding Berlin negotiations with Nazi economic officials
  in April 1933 and did not live to see the agreement signed; it was finalized by Eliezer
  Hoofien of the Anglo-Palestine Bank. Fixed in both places — this is the second dated-after-death
  class of error found in the project (first was the Weitz "chaired" overstatement last round;
  this one is more serious since the date itself was simply wrong, not just imprecise).

Full collision check clean. **Citation tally across all 6 data files** (requested by Nick):
107 UNVERIFIED / 56 VERIFIED before this round; historical_actors.json specifically improved
from 8/38 to 12/34 VERIFIED/UNVERIFIED. Full breakdown:

| File | UNVERIFIED | VERIFIED | % verified |
|---|---|---|---|
| historical_actors.json | 34 | 12 | 26.1% |
| organizations.json | 44 | 23 | 34.3% |
| topics.json | 20 | 24 | 54.5% |
| laws.json | 2 | 2 | 50.0% |
| knesset_members.json | 2 | 0 | 0.0% |
| current_foreign_actors.json | 0 | 0 | n/a (no citation field in use) |
| **Total** | **102** | **61** | **37.4%** |

historical_actors.json remains the weakest file by a wide margin and the clear next-round
priority; knesset_members.json's 2 entries (Kaplan/Eshkol) have never been touched.

## historical_actors.json fully verified (2026-09-01) — Nick authorized unattended continuation

Nick asked to leave verification running file-by-file until either everything's verified or the
Knesset scrape finishes, without needing to be asked again each round. Worked through all 24
remaining UNVERIFIED `key_land_actions` in `historical_actors.json` across several batches
(checkpointed with a collision check + republish partway through, then finished the rest):
Hankin's Jezreel dunam range (widened — sources actually range 176,000 to 368,526 dunams
depending on scope, not the narrower 200-240K previously guessed), Rothschild's PICA founding
and 1880s-90s colony rescues (Rishon LeZion, Zichron Ya'akov, Rosh Pinna, Ekron; £5M+ total),
Ruppin's PLDC/Tel Aviv/Degania roles, Ussishkin's JNF tenure, Moses Hess, Kalischer, Pinsker's
Kattowitz Conference, Herzl's El-Arish/Uganda Scheme and First Congress, Nordau (a real
correction: he became Congress *president* from 1905, not vice-president throughout, as
previously written), Schapira's JNF proposal, Ahad Ha'am, Belkind's Bilu landing (6 July 1882,
14 Kharkiv students), A.D. Gordon (a real correction: joined Degania specifically in 1911, not
continuously from 1904 as implied — he first worked at Petah Tikva), Katznelson's Histadrut,
Weizmann/Sokolow/Balfour's Balfour Declaration roles (Sokolow's Cambon letter enriched with its
actual 4 June 1917 text), Jabotinsky's Revisionist Zionist Alliance (tightened to 25 April 1925,
Paris), Ben-Gurion's Jewish Agency chairmanship and Declaration of Independence, Golda Meir's
Abdullah meeting and premiership settlement record (Kiryat Arba, ~10 Jordan Valley settlements,
4 rebuilt Etzion Bloc settlements, 5→14 settlement growth), Yosef Weitz's JNF tenure, Silver's
AZEC/lobbying record, the Shochats' Bar-Giora/Hashomer founding (28 Sept 1907) and Sejera
commune, Sadeh (a real correction: commanded Palmach only 1941-45, then became Haganah Chief of
Staff — not continuously through 1948 as previously implied), Dayan's Six-Day War role, Begin's
settlement acceleration (the actual 1979-83 master plan figures: 46 new settlements/16,000
families), Sharon's Agriculture Ministry and 1982 Lebanon invasion/Sabra-Shatila/Kahan Commission
record, and Borochov's "Our Platform."

**Real corrections found this push (not just enrichment), for the record:** Nordau's
vice-president-vs-president Congress role, A.D. Gordon's Petah Tikva-then-Degania sequence, and
Yitzhak Sadeh's 1945 Palmach-to-Haganah-Chief-of-Staff handover. None change this dataset's
land-impact conclusions, but all three would have stated something specifically wrong if left
uncorrected.

Full collision + dangling-reference check clean throughout, republished at the same URL after
the halfway checkpoint and again on completion. **`historical_actors.json`: 0 UNVERIFIED, 34/34
VERIFIED — the first data file to reach 100%.**

## organizations.json fully verified (2026-09-01) — second file to reach 100%

Continued the unattended verification sweep into `organizations.json` (44 UNVERIFIED at the
start of this file). Worked through every remaining entry — Haganah, Irgun, Lehi, Herut, Likud,
Kadima, IDF, Poalei Zion, Ahdut HaAvoda, Mapai, Israeli Labor Party, South Lebanon Army, Hapoel
Hatzair, Yishuv, State of Israel, Knesset, WZO, JNF, PLDC, Hovevei Zion, Jewish Agency for
Palestine, Bilu movement, Histadrut, Asefat HaNivcharim, Va'ad Leumi, Custodian of Absentee
Property, United Nations, and the new Prime Minister of Israel entry — largely by direct live
search, with a good number resolved by cross-referencing facts already verified in this same
session's `historical_actors.json` pass (Bar-Giora/Hashomer via Yisrael Shochat's entry, Poalei
Zion's Borochov synthesis via his entry, WZO/JNF/PLDC via Herzl/Schapira/Ruppin, State of
Israel/Va'ad Leumi via Ben-Gurion's Declaration entry, Custodian of Absentee Property via the
already-verified law itself).

**Five real corrections found (not just enrichment):**
- **Haganah's founding date** was off by two weeks (1 June 1920 vs. actual 15 June 1920).
- **Herut's founding date and its causal framing were both wrong** — dated to 1 June 1948 and
  described as founded *after* the Altalena Affair/Irgun's dissolution. Actual founding is
  15 June 1948, which is *before* the Altalena Affair (20-23 June) and Irgun's formal disbandment
  (September 1948) — the causal sequence in the old text ran backwards.
- **The Irgun's 1931 founding was described as Revisionist-aligned from day one**; it actually
  became the Revisionist movement's militia only in 1936-37 under Jabotinsky — its actual 1931
  founder was Avraham Tehomi, not the Revisionist movement.
- **South Lebanon Army's action_record date range (1985-1999) contradicted the org's own
  `dissolution_date` field (2000-05)** — an internal inconsistency, not just an unsourced claim;
  corrected to match, with the actual 22 May 2000 collapse date added.
- **A house-style violation slipped through**, unrelated to citation accuracy: the Jewish Agency
  for Palestine's description directly named a sibling data file in reader-facing text
  (`current_foreign_actors.json`) — the exact "encyclopedia, not a database skin" mistake fixed
  project-wide weeks ago, missed here since this org was added afterward. Fixed.

Also gave the Prime Minister of Israel's post-1967 settlement-authority claim (previously left
deliberately hedged) real anchor facts: Eshkol's cabinet approved Merom Golan (mid-July 1967,
first Golan settlement) and Kfar Etzion (September 1967, first West Bank settlement, approved
despite legal advice that it would violate the Fourth Geneva Convention) — upgraded from
interpretive hedge to a sourced, concrete institutional pattern.

Full collision + dangling-reference check clean throughout, checkpointed and republished twice
during this push, final republish on completion. **`organizations.json`: 0 UNVERIFIED, 35/35
VERIFIED.** Two of six data files now fully verified.

## Every citation in the dataset now verified (2026-09-01) — the verification sweep's finish line

Continued straight from `organizations.json` into the remaining two files without pausing:

**`topics.json` (20 UNVERIFIED → 0).** Enriched the Jezreel Valley/Sursock family pair with the
family's actual acquisition history (1872 Ottoman purchase, ~400,000 dunams, £20,000, under the
1858 land reform; ~8,000 tenant farmers across 22 villages eventually evicted) and the family's
own origin story (Beirut since 1712, 1858 land-reform beneficiaries). Verified all five Aliyah
waves' immigrant counts and defining facts. **Two real corrections, not just enrichment:**
Rishon LeZion's founding was credited to "mostly the Bilu movement," but Bilu didn't found it —
Hovevei Zion pioneers under Zalman Levontin did, on 31 July 1882; Bilu's members joined
afterward as hired laborers (consistent with Israel Belkind's own already-verified entry). And
the Ottoman Palestine entry's claim that the 1858 Land Code "concentrated registered title in
notables'/absentee hands" turned out to be a real but non-universal pattern — a property-records
survey of the Jerusalem hill country specifically found peasants registering land in their own
names there, not a single notable/moneylender doing so — added as an honest regional caveat
rather than smoothed over. Also verified the Iron Wall doctrine's exact publication (4 November
1923, Rassvet, with its follow-up essay a week later) and cross-referenced Auto-Emancipation,
Kattowitz Conference, First Zionist Congress, and Balfour Declaration against already-verified
actor entries.

**`knesset_members.json` (2 UNVERIFIED → 0) — never touched before, and it had a real,
concrete error.** Both Kaplan and Eshkol's entries still carried the original wrong Sefer
HaChukim citations ("vol. 4, p. 68" / "vol. 5, p. 155") that were corrected in `laws.json`
months ago — this file was simply never synced when that fix landed. Corrected both to match
(No. 37 p. 86 / No. 122 p. 58) and added verified biographical detail for both men (Kaplan:
born Minsk, 1891-1952, Jewish Agency treasurer 1933-48; Eshkol: born Levi Shkolnik, Oratovo,
1895, later Israel's third Prime Minister). Their individual roll-call votes remain honestly
unconfirmable — this project's own scraper build already established that no per-member vote
data exists for any Knesset before the 16th, a structural gap, not a research shortfall.

Full collision + dangling-reference check clean on every batch. **Final tally, checked
programmatically across all six files: 0 UNVERIFIED, 158 VERIFIED — 100% of citations in the
dataset are now verified**, reached before the Knesset scraper finished (96.0% at last check).
Republished at the same URL as the final state.

**Recurring lesson across this whole sweep, worth keeping in mind for future content:** a
non-trivial share of what got "corrected" wasn't sourcing at all — it was internal consistency
(dates that contradicted each other across two entries, or a causal sequence that ran backwards
once the real dates were known). Checking a fact in isolation against a search result catches
less than checking whether it's consistent with everything else already in the dataset.

## Knesset scrape complete + first scraper-sourced MK entry (2026-09-01)

The full vote_results pull finished: **1,953,709 / 1,953,709 rows (100%)**, confirmed against
the target directly. Nick asked to watch for completion and start the SQLite →
`knesset_members.json` transformation once it landed.

**Built `scripts/promote_vote.py`** — the second half of the research pipeline
`find_land_votes.py` started: given a `vote_id`, it prints the full roll call (grouped by
result, with each MK's party-at-the-time via `mk_party_membership`), with `--mk-name` and
`--against-only` filters for quickly checking one person's vote. Deliberately does not
auto-generate `knesset_members.json` entries — same discipline as everywhere else in this
project: a human (or Claude, reviewing) still writes the `land_impact` description and
citation by hand, the script just makes the underlying roll call fast to check instead of
writing ad hoc SQL every time.

**Promoted the first entry actually sourced from the scrape itself**, not hand-researched from
scratch: **Reuven Rivlin**, added to `knesset_members.json` as a calibration case for how future
promotions should look. Picked from `find_land_votes.py`'s "settlement" candidate list — vote
4138, the 16 February 2005 Disengagement Plan Implementation Law, the law authorizing the Gaza
withdrawal already covered from the executive side in Ariel Sharon's own actor entry. Rivlin,
then a sitting Likud MK and Knesset Speaker, was one of 17 Likud MKs who voted against their own
Prime Minister's bill — a real backbench rebellion the bill's 59-40-5 passage depended on
opposition support to overcome. He later became Israel's tenth President (2014-2021), so also
added him to the President of Israel and Likud orgs' `notable_members`, plus a new action_record
entry on the President of Israel org for his 2014 election.

**Independent confirmation the scrape data itself is accurate:** the scraped vote_results
roll call for vote 4138 gives exactly 59 For / 40 Against / 5 Abstain — live search independently
corroborates that same 59-40-5 tally from Jewish Virtual Library's own account of the vote,
matching exactly. First real end-to-end validation that this project's own scraped data agrees
with outside sourcing, not just internally consistent.

Deliberately did not try to promote all 720 candidate votes or scale to more MKs this round —
picking who's independently notable enough to warrant a full entry is an editorial judgment call,
not a mechanical one, so this establishes the pattern with one clean example rather than
guessing how far to scale unprompted. Full collision + notable_members-reference check clean,
republished at the same URL.

## Land/demographic policy ledger — laws + first MK "For" voter batch (2026-09-01)

Nick asked for two things at once: (1) a ledger of laws designed to separate Palestinians from
their land, deny return, expand imprisonment, resettle in Israel's demographic favor, or
otherwise expand Israeli territory/reduce Palestinian statehood prospects; and (2) any/all MKs
who voted for land-taking or against protecting/returning Palestinian land. Scoped both the same
way everything else in this project has been built — real research, real citations, in batches,
not a blind dump.

**10 new laws added to `laws.json`** (2 → 12 total): Emergency Land Requisition Law (1949),
Prevention of Infiltration Law (1954, criminalizes refugee return), Golan Heights Law (1981),
Basic Law: Jerusalem (1980), Citizenship and Entry into Israel Law / "Family Unification ban"
(2003), Admissions Committees Law (2011), Settlements Regularization Law (2017, retroactively
legalizes West Bank outposts on private Palestinian land), Kaminitz Law (2017, planning
enforcement disproportionately hitting Arab/Palestinian construction), Basic Law: Israel as the
Nation-State of the Jewish People (2018, Article 7 names Jewish settlement a constitutional
national value). Also added the companion Resolution 497 (Golan Heights, unanimous 17 Dec 1981,
"null and void," US-vetoed follow-up) — the same UN-response pattern as Resolution 478/Jerusalem.

**Real design fix caught before publishing:** several new law entries put hedge text like
"UNVERIFIED — best guess..." directly into the `official_citation`/`sponsoring_ministry` fields,
which the wiki renders as if it were the actual citation/ministry name. Nulled those out
(matching how `estimated_hectares_affected: null` already works elsewhere) and kept the honest
hedge only in the dedicated `citation` field, where it belongs.

**New actor: Benjamin Netanyahu** — absent from the dataset entirely despite being the sponsoring
PM behind 3 of the 10 new laws (Regularization, Kaminitz, Nation-State). Added to
`historical_actors.json` (not `knesset_members.json` — matching how every other PM in this
dataset lives there) with those 3 laws as key_land_actions. Living-person discipline applied:
documented governmental actions only, explicitly scoped to the well-settled 2017-18 period, no
claims about his status beyond that.

**8 new MKs added, all "For" voters on 2011-2018 expansion/exclusion laws**, picked from the full
roll calls for being independently notable (party leaders, ministers, later heads of state) with
multi-vote records across these bills: Naftali Bennett, Ayelet Shaked, Bezalel Smotrich, Avigdor
Liberman, Yariv Levin (voted For on all 4 of the 2011-2018 bills tracked here — the only one so
far), Ze'ev Elkin (held the Jerusalem Affairs and Settlements portfolio — the ministry most
directly named for this dataset's subject), Tzipi Hotovely, Miri Regev. All sourced from this
project's own completed vote-results scrape, not hand-research — each is a real named
person_id/vote_id pair, independently spot-checked against external sourcing for the 4 bills'
overall tallies (all matched exactly, same validation pattern as the Rivlin entry).

**Real bug caught before publishing: Netanyahu was accidentally added to *both*
`historical_actors.json` and `knesset_members.json`** — a genuine duplicate-person collision the
collision-check script caught immediately (`personLink()` checks both files by design specifically
because a person should live in exactly one). Fixed by removing the MK-file entry and folding
its scrape-verified vote confirmation into the existing actor entry instead. Also fixed a stale
house-style slip in the Rivlin entry (a literal sqlite filename in citation text, from before the
"no data filenames in reader-facing text" sweep).

**Scale reality check, worth being upfront about:** the four bills' full "For" roll calls total
~190 individual votes (Nation-State 62, Regularization 60, Kaminitz 43, Admissions Committees
35, with real overlap between bills). This batch covers 8 of them — the ones independently
notable enough to research properly. Full "any/all" coverage of every backbencher who voted this
way, across these 4 bills plus the ~715 other candidate votes `find_land_votes.py` surfaces,
would be many more rounds of the same per-person research (each requires English name/birth
details a Hebrew-only roster doesn't supply) — this is the honest scope of "any or all," not
something a script can shortcut. Continuing on request.

Full collision + dangling-reference + notable_members/sponsoring_mk_id-reference check clean.
35 orgs (Likud and Prime Minister of Israel notable_members updated), 35 actors, 12 laws,
11 knesset_members, 45 topics.

## Netanyahu verification + 9 requested entities (2026-09-01)

Nick asked to verify Netanyahu rendered correctly (he'd seen him listed somewhere and worried
about a duplicate) and to add 8 named entities if missing.

**Netanyahu check:** confirmed via the local rendered page and direct source inspection —
he appears exactly once, correctly under Historical Actors, not under Knesset Members. The
fix from the previous round held; no duplicate found. (If Nick was looking at a browser tab
from before that fix landed, a hard refresh of the artifact should resolve it.)

**None of the 8 requested items existed yet** — added all of them:
- **Anwar Sadat** and **Jimmy Carter** (`historical_actors.json`) — the schema has always covered
  foreign actors (Balfour, Rothschild), so both fit cleanly. Carter's entry includes his 2006
  book 'Palestine: Peace Not Apartheid,' directly relevant to this dataset's West Bank/settlement
  subject matter, not just the Camp David brokering.
- **Itamar Ben-Gvir** (`historical_actors.json`, not `knesset_members.json`) — checked his scraped
  vote history first (`find_land_votes.py --mk 30811`, 0 hits — he entered the Knesset in 2021,
  after this dataset's tracked land-vote candidates) and placed him with Netanyahu instead,
  documenting his National Security Ministry actions (Dec 2022 appointment, post-Oct-2023 gun
  license relaxation for settlers, the June 2025 UK/Canada/Norway/Australia/NZ sanctions).
  Same living-persons discipline as Netanyahu: documented actions only.
- **Gahal** and **Movement for Greater Israel** (`organizations.json`) — both had been sitting as
  known gaps for a long time, explicitly flagged as "not yet profiled" in Likud's own lineage
  since early in the project. Added both properly and updated Likud's `predecessor_orgs` to
  reference them as real org_ids instead of placeholder text.
- **Jewish Home, National Union, Yamina, Religious Zionism** (`organizations.json`) — the four
  parties referenced only as free-text strings inside the new MKs' `knesset_terms` from the last
  round. This is a genuinely lattice-shaped merger/split history, not a clean chain (Jewish Home
  → Yamina and → Religious Zionism; National Union → Jewish Home *and* feeds into Religious
  Zionism separately) — modeled as cleanly as the schema's single-predecessor-chain shape allows,
  with the fuller picture spelled out in each entry's own description text.

Full collision check caught one real gap during this batch: Jewish Home's `predecessor_orgs`
listed bare `"Tkuma"` without the `"(not yet profiled)"` marker the same list's other two entries
used, which the checker read as a broken reference. Fixed for consistency.

38 actors, 41 orgs, 11 knesset_members, 12 laws, 45 topics. Full collision + dangling-reference +
notable_members/sponsoring_mk_id-reference check clean.

## Netanyahu/Ben-Gvir moved to Knesset Members + ledger expansion (2026-09-01)

Nick asked to swap Netanyahu and Ben-Gvir from `historical_actors.json` into
`knesset_members.json`, and to keep expanding the MK ledger.

**Migration:** removed both from `historical_actors.json`, added to `knesset_members.json`.
Netanyahu now carries his 2 already-verified scraped votes (Nation-State Law, Kaminitz Law, both
For) plus the Regularization Law recorded as a government-sponsorship "Executive Action" (no
personal floor-vote record found in the scrape for that specific bill — noted honestly rather
than invented) across his full 12th-25th Knesset term history. Ben-Gvir's 3 documented ministerial
actions ported over unchanged, recategorized as "Executive Action"/"N/A for Non-Legislative" per
the MK schema's own support for non-legislative entries — confirmed via `find_land_votes.py --mk`
that no matching floor vote exists for him in this dataset's tracked bills (he entered the Knesset
in 2021, after the 2011-2018 bills already covered). Both actor_ids stayed the same, so every
existing cross-reference (Likud, Prime Minister of Israel notable_members, laws'
`sponsoring_mk_id`) resolved automatically to the new MK entries with no broken links.

**5 new MKs added to the ledger**, found via the existing 4 bills' rolls plus a newly-discovered
2023 vote: Yuli Edelstein (5 votes — the fullest record in the ledger so far, spanning 2005-2023,
including voting *against* the original Disengagement Law and *for* repealing part of it 18 years
later — a coherent single-position arc, not a contradiction), Tzachi Hanegbi (4 votes, a genuine
contrast recorded honestly — voted *for* the 2005 withdrawal as a Kadima member, then *for* all
three 2017-18 expansion bills after returning to Likud), Israel Katz (3 votes, same honest
for-then-against-then-for-expansion pattern as Hanegbi), Simcha Rothman and Limor Son Har-Melech
(both via the new **northern West Bank re-entry vote**: a 21 March 2023 amendment repealing the
2005 Disengagement Law's ban on Israelis entering/residing in the four evacuated northern West
Bank sites, passed 31-18 — Son Har-Melech is a former Homesh resident and Homesh First co-founder
voting to repeal the ban on returning to the exact land she was evacuated from, arguably the most
directly personally-interested vote in the whole ledger).

**Real data-quality finding, documented rather than smoothed over:** for this new 2023 vote,
Rothman's and Son Har-Melech's vote_results rows use different internal person_ids (32700 and
34372) than their `mk_roster` entries (30812 and 30849) — the roster IDs have zero vote rows,
the vote-results IDs have thousands. A genuine ID-space mismatch specific to Knesset 24-25
freshmen in this project's own scraper build, not previously encountered in earlier, longer-
serving MKs. Used the vote-results IDs (unambiguous by exact name match) and flagged the
discrepancy honestly in both citations rather than silently picking one.

38→36 actors, 41 orgs (Likud, Kadima, Religious Zionism notable_members updated), 18 knesset
members (11→18), 12 laws, 45 topics. Full collision + dangling-reference +
notable_members/sponsoring_mk_id-reference check clean throughout.

## Bill expansion + full ledger sweep across sovereignty bills (2026-09-01)

Nick asked to expand the set of bills being tracked, then get names on all of them. Found and
verified 4 new, very recent Knesset sovereignty/annexation bills via broadened keyword search,
each cross-checked against live press reporting before being trusted:

- **Jordan Valley Sovereignty Bill (15 March 2023)** — Liberman's bill, defeated 65-14; the
  coalition's own hardline parties (Otzma Yehudit, Religious Zionism) voted it down alongside
  everyone else, read by a rival Likud MK as denying Liberman political credit rather than
  opposing sovereignty itself.
- **Ma'ale Adumim Sovereignty Bill (22 October 2025)** — Liberman's bill for the E1-corridor
  settlement, passed a preliminary reading 31-9 (press reports 32-9, a minor unreconciled
  variance) despite the government's own request to withdraw it, then frozen by the coalition
  rather than advanced.
- **Judea and Samaria Sovereignty Bill (22 October 2025, plus a 2021 predecessor)** — Avi Maoz's
  bill extending Israeli law across the whole settled West Bank, passed by a single vote, 25-24,
  with only one Likud MK (Yuli Edelstein) defying Netanyahu's own directive to vote for it, and
  several UTJ MKs including party leader Yitzchak Goldknopf voting for it too. A 2021 version of
  the identical bill had been defeated 64-50 — real, if inconsistent, momentum since.
- **Beitar Illit Sovereignty Bill (31 December 2025)** — defeated 45-8, unlike its October
  cousins; support for single-settlement sovereignty bills in this wave was genuinely
  inconsistent, not a simple escalating trend.

New topic_type `"Legislative Proposal"` added (documented in SCHEMA.md) for bills that haven't
become enacted law — kept separate from `laws.json`, which stays reserved for actually-enacted
statutes with a real official citation.

**Real bug found and corrected: the "no floor vote found" claims for Ben-Gvir, Rothman, and
Son Har-Melech in the last round were wrong**, caused by the same roster-ID/vote-ID mismatch
already flagged for Rothman/Son Har-Melech — but not yet checked for Ben-Gvir, whose original
`find_land_votes.py --mk 30811` search used his roster ID, which has zero vote rows. Re-run
against his real vote-casting ID (32689, confirmed via the same person appearing in a fresh
vote's roll call) turned up 47 land-relevant votes, including two "For" votes on the Judea and
Samaria Sovereignty Bill (2021 and 2025) — both now added, replacing the incorrect "no vote"
framing with real floor votes. This is now the second and third confirmed instance of this
specific ID-mismatch pattern, consistently limited to Knesset 24-25-era MKs; **worth remembering
for any future promotion: always try both a `--mk` search on the roster ID and a name-based
search across `vote_results` directly before concluding no vote exists.**

**Full ledger sweep across all 6 existing MKs with a plausible stake in the new bills** —
Edelstein, Ben-Gvir, Rothman, Son Har-Melech, Liberman, and Elkin — each checked against all 4
new bills and updated with every additional vote found (Liberman alone gained 4: sponsor votes
on both his own Jordan Valley and Ma'ale Adumim bills, plus Judea/Samaria and Beitar Illit).

**5 new MKs added**, each a real floor vote on one of the new bills: Yair Lapid and Benny Gantz
(both opposition leaders who voted *for* the Ma'ale Adumim bill — a genuine complication of any
simple coalition/opposition reading of this legislative wave), Gideon Sa'ar (Jordan Valley bill,
now Foreign Minister), Avi Maoz (the Judea/Samaria bill's own sponsor, with a 2021-2025 voting
history spanning both versions), Yitzhak Goldknopf (UTJ leader and Housing and Construction
Minister — the ministry most directly on-topic of any portfolio in this dataset). Gantz, Maoz,
and Goldknopf all share a milder version of the same data gap: their `mk_terms`/
`mk_party_membership` records are entirely empty in this project's scrape despite having real
vote-casting IDs, so their party/term context is reconstructed from live search rather than the
database — flagged honestly in each citation rather than silently filled in.

Full collision + dangling-reference + notable_members/sponsoring_mk_id-reference check clean.
41 orgs (Likud, Religious Zionism notable_members updated), 23 knesset_members (18→23), 49
topics (45→49, the 4 new bills), 12 laws, 36 actors.

## ID-mismatch sweep completed (2026-09-01)

Nick: "Both — sweep the rest, then keep pulling more bills," in response to being offered the
choice. Completed the "sweep" half first.

**Mirror-image version of the Ben-Gvir/Rothman/Son Har-Melech bug found for Gantz, Maoz, and
Goldknopf.** The earlier fix pattern was: roster ID has term/party data, vote ID (different
number) has the actual votes. For these three it runs backwards — their vote-casting IDs
(32007, 32696, 34370, already used correctly for the votes already in the ledger) have **empty**
`mk_terms`/`mk_party_membership` rows, which is what forced the "reconstructed from live search"
hedge language in the previous batch. Searched `mk_roster` directly by Hebrew surname and found
each has a separate, roster-only person_id with real term/party data: Gantz 30657 (Knesset
21-25, Blue and White → National Unity at 25), Maoz 30814 (Knesset 24-25, Religious Zionism →
Noam), Goldknopf 30846 (Knesset 25, United Torah Judaism, across two disjoint date ranges —
2022-11-15 to 2023-01-06, then 2025-06-15 to present — reason for the gap not yet researched,
noted rather than smoothed over). Updated all three `knesset_terms` fields with the real data
(Gantz's grew from 1 entry to the full 5-term history) and rewrote all three citations to
explain the split plainly instead of claiming no data exists.

**Ran `find_land_votes.py`'s full keyword sweep against the confirmed-correct vote-casting ID
for every other MK in the ledger** (Rivlin, Bennett, Shaked, Smotrich, Liberman, Levin, Elkin,
Hotovely, Regev, Netanyahu, Edelstein, Hanegbi, Katz, Lapid, Sa'ar, plus Gantz/Maoz/Goldknopf on
their correct IDs) to check for any further ID-mismatch surprises. None found — every one of
these IDs already returns real vote data, confirming the roster-ID = vote-ID list from the
previous batch was correct and the mismatch bug is now fully accounted for across the ledger.

The same sweep also returned each MK's full keyword-matched vote count, and it's worth recording
honestly why this didn't turn into a promotion batch: counts ranged from 12 (Goldknopf, barely
into his second term) to 283 (Levin, decades in the Knesset) — Rivlin 235, Edelstein 255, Elkin
242, Katz 232, Sa'ar 227, Netanyahu 195, Regev 156, Hotovely 151, Hanegbi 145, Bennett 81,
Liberman 89, Lapid 95, Smotrich 75, Shaked 70, Gantz 42, Maoz 33. Unlike the Ben-Gvir case —
where the count went from 0 (wrong ID) to 47 (right ID), a clear signal of a real gap — these are
long careers hit by broad keyword terms (`ריבונות`/sovereignty, `קרקע`/land) that surface plenty
of noise: budget line items, unrelated planning bills, procedural motions. Promoting from a list
like that responsibly means reading each roll call, not batch-converting hit counts into entries,
so it's being treated as backlog to work through opportunistically — pulled in as specific bills
get added, the way this ledger has actually grown so far — rather than force-promoted wholesale
in one pass just because the search returned it.

Full collision + dangling-reference check clean. 23 knesset_members (unchanged count, 3 entries
corrected), all other files unchanged this batch. Re-embedded and republished.

## More bills: 2022 dissolution-day votes + Heritage Authority Bill (2026-09-01)

Second half of "sweep the rest, then keep pulling more bills." Mined the scraped vote corpus
directly (not just per-MK) for new candidate bills via annexation/sovereignty keyword search
across all vote titles, then verified the strongest hits against live press before adding
anything.

**Found a real episode missed until now: two competing Judea/Samaria sovereignty bills — one
sponsored by Likud MK Shlomo Karhi — brought to snap votes on 22 June 2022, hours after the 24th
Knesset had already voted to dissolve itself for new elections.** Religious Zionism leader
Bezalel Smotrich was quoted urging colleagues "there is no reason now not to vote your
conscience" now that coalition discipline no longer applied. Both bills still failed, 46-52 and
46-51 (Jerusalem Post, cross-checked exactly against the scrape). Rather than spin up a wholly
separate topic for what is substantively the same recurring proposal, folded this into the
existing "Judea and Samaria Sovereignty Bill" topic entry as a third documented attempt between
the already-tracked 2021 and 2025 votes — the four attempts now trace a real trajectory (14-point
defeat → two narrower defeats on a whip-collapsed day → eventual single-vote passage). **9 MKs
already in the ledger get a new vote entry each** (Netanyahu, Smotrich, Ben-Gvir, Rothman, Katz,
Hanegbi, Levin, Regev, Edelstein) — all voted "For" on both bills, confirmed via each person's
already-established correct vote-casting ID. Kept as one combined entry per person (citing both
vote_ids) rather than two near-duplicate entries, a deliberate compression choice given how close
in time and substance the pair is.

**New bill, new type of encroachment for this ledger: the Judea and Samaria Heritage Authority
Bill (12 May 2026).** Sponsored by Likud MK Amit Halevy, creates a Israeli civilian authority
over West Bank antiquities/archaeology/heritage sites — critics call it de facto annexation by
administrative rather than declarative means, since it transfers what was a military-government
function into civilian Israeli hands without a formal sovereignty vote. Passed first reading
23-14, with a companion Antiquities Authority jurisdiction amendment passing 22-14 same session —
both confirmed against the scrape exactly matching Times of Israel's reporting, including
Halevy's quoted rationale ("The current war is about our identity, our culture, about God, about
our deep belonging to this land"). **New MK: Amit Halevy** — his own individual roll-call row
wasn't pinned to a specific vote-casting person_id (the roster-ID/vote-ID split turns out to
affect most voters on this particular bill, not just a handful of named people, and chasing every
one down wasn't worth it for a sponsorship-level entry already solidly corroborated by press);
his term history (Knesset 23, gap, Knesset 25 from Jan 2023) came cleanly from his roster ID
(30711). **Son Har-Melech gets a new vote entry too** — a former Homesh resident voting for a
bill extending Israeli civilian authority over West Bank heritage sites fits her established
pattern in this ledger.

Full collision + dangling-reference check clean. 24 knesset_members (23→24), 41 orgs (Likud's
notable_members +1), 50 topics (49→50, Heritage Authority Bill + the existing sovereignty-bill
topic's history extended), 11 laws, 36 actors unchanged. Re-embedded and republished.

**Scale reality check, same honesty as prior rounds:** the annexation/sovereignty keyword search
on the full vote corpus (not just per-MK) surfaced several more candidates not pursued this round
— a 2020 outposts government-funding bill, a 2023 Basic Law: Referendum amendment requiring a
referendum before applying sovereignty (procedural, cuts against rapid unilateral annexation
rather than for it, so likely doesn't fit this ledger's inclusion criteria — not added, flagged
rather than silently dropped), and several more single-settlement/border motions further back in
the record. Continuing on request, same pattern: research → verify → add, not a blind sweep.

## Prawer-Begin Bill + East Jerusalem residency revocation law (2026-09-01)

Nick: "keep pulling more bills." Broadened the keyword sweep on the full vote corpus beyond
sovereignty/annexation into new categories matching Nick's original scope brief (separating
Palestinians from land, denying return, expanding imprisonment, resettling communities):
outposts funding, administrative detention, family unification, Greater Jerusalem/E1, Area C,
Bedouin/Negev relocation, prisoner release. Two real, well-documented bills stood out and were
added after live-press verification:

**Bedouin Settlement Regularization Law, aka the Prawer-Begin Plan (2013)** — a government bill
to resolve Negev Bedouin land claims by relocating an estimated 30,000-40,000 Bedouin citizens of
Israel into planned townships, compensating up to 50% of claimed land. Passed a first reading
43-40 on 24 June 2013 (matches the scrape exactly), then withdrawn by the government six months
later after mass protests including a nationwide "Day of Rage" — never enacted, so added as a
`topic_type: "Legislative Proposal"` rather than to `laws.json`, same treatment as the sovereignty
bills. Distinct from the West Bank bills elsewhere in this ledger: targets Bedouin citizens of
Israel proper, not occupied-territory Palestinians, but the same underlying pattern (resolve land
claims by moving the claimants). **8 MKs checked, 7 get a new "For" vote**: Katz, Levin, Regev,
Edelstein, Rivlin, Bennett, Sa'ar (as sitting Interior Minister at the time, confirmed 18 March
2013 - 5 November 2014 tenure, a directly-responsible portfolio) — Shaked was also checked but has
no roll-call row on either new bill and was correctly left untouched. Rivlin's "For" vote as
Knesset Speaker is recorded plainly rather than smoothed over, a genuine data point against his
later, more consensus-minded reputation as President.

**Entry into Israel Law (Amendment No. 30), 2018 — East Jerusalem/Golan permanent-residency
revocation.** A real enacted law (unlike Prawer, added to `laws.json`): authorizes Israel's
Interior Minister to revoke Jerusalem/Golan permanent residents' status for "breach of
allegiance," drafted in direct response to a September 2017 Supreme Court ruling that had just
reinstated four East Jerusalem Palestinian politicians' residency after the Interior Ministry
tried to revoke it administratively — the amendment gave by statute what the Court had just
denied by executive fiat. Final reading passed 48-18-6 on 7 March 2018 (live-search only — this
project's scrape only captured an earlier 3 January 2018 reading, 63-17, under the same bill
title; the two readings' tallies aren't reconciled, noted honestly in the citation). No official
Sefer HaChukim citation number found via search; left `null` rather than guessed, per this
project's standing citation discipline (the same lesson from the first verification pass, where a
guessed citation was simply wrong). **9 MKs get a new "For" vote** on the January reading: Bennett,
Smotrich, Elkin, Hotovely, Netanyahu, Edelstein, Hanegbi, Katz, Levin.

Full collision + dangling-reference check clean. 24 knesset_members (unchanged count, 12 entries
gained new vote records), 41 orgs, 51 topics (50→51, Prawer-Begin Bill), 12 laws (11→12, Entry
into Israel Amendment 30), 36 actors unchanged. Re-embedded and republished.

**Still flagged, not yet pursued:** administrative-detention search returned zero title hits
(may need different Hebrew phrasing — Knesset votes on detention are often procedural/committee
matters rather than plenum floor votes with searchable titles); Area C search also returned
nothing under that exact phrasing; two further Bedouin-sector Planning and Building Law
amendments (2006 master-plan, 2011/2012 demolition-order provisions) were found but not yet
verified/added — real candidates for a future round.

## Chased the two Bedouin planning-law leads — real dead end, not added (2026-09-01)

Nick asked to chase the 2006 and 2011/2012 Bedouin-sector Planning and Building Law amendments
flagged last round. Pulled the `votes` table's `vote_subject_he` field (not previously checked)
and found both are procedural-stage votes, not substantive passage votes: the 2006 vote (19-45-5)
was "include the topic on the plenum's agenda"; the 2012 vote (31-1) was "refer the bill to a
committee." A third, earlier attempt at the same demolition-orders bill in 2003 was voted "remove
from the agenda" — three different Knessets, same bill stalling at the earliest possible stage
each time, never reaching a real first reading in the scraped data.

**Worse, the 2006 vote's actual coalition looks like the opposite of what the title suggested:**
the "For" side (wanting it debated) was Rivlin, several Haredi MKs, and the Arab-party bloc
(Bishara, Zahalka, Barakeh, a-Sana); the "Against" side (blocking it) was Netanyahu, Olmert,
Livni — the government mainstream of the day. That pattern reads like the government blocking a
pro-recognition bill, not sponsoring a land-taking one — live search on the bill's actual content
was inconclusive and risked conflating it with differently-titled bills sharing similar names.
**Decided not to add either bill or any MK votes** — recording a committee-referral or
agenda-placement vote as if it were a substantive "for/against the policy" vote would misrepresent
procedure as position, and the 2006 bill's direction isn't confidently established either way.

**Standing lesson for future rounds: check `vote_subject_he` before treating any vote as
substantive, not just the bill title.** Titles alone can't distinguish a real passage vote from an
agenda/procedural motion, and — as this round showed — coalition voting patterns on a procedural
motion can look like normal politics while actually running in the opposite direction from the
bill's content. No data files changed this round.

## Confirmed the 2006 bill's direction via primary source, found a real new bill (2026-09-01)

Nick: "can we do both?" — pin down the 2006 bill's real direction, and pull a fresh category of
bills, in the same turn.

**Pinned down the 2006/2011/2012 Bedouin bills' direction directly from the Knesset's own OData
API — not press, primary source.** Fetched each vote's `ItemID` -> `KNS_PlmSessionItem` ->
`KNS_Bill` -> `KNS_BillInitiator` chain and found: all three (plus a 2003 predecessor found along
the way) were **private member's bills sponsored by Arab/Hadash MKs** — the 2006 master-plan bill
by Talab a-Sana (with Ahmad Tibi, Ibrahim Sarsur, Abbas Zakur as co-signers), the 2011/2012 bills
by Mohammed Barakeh (with Hanna Sweid, Dov Khenin, Afou Agbaria) and by Talab a-Sana again. This
settles it: these were very likely protective/recognition-seeking bills from exactly the MKs who
champion Bedouin land rights, not government land-taking bills — confirming the coalition-pattern
suspicion from last round with hard sponsor data rather than a guess. Correctly left out of the
ledger; the primary-source bill-initiator lookup (`KNS_BillInitiator` filtered by `BillID`) is
now a standing technique worth using whenever a bill's political direction is ambiguous from its
title alone — more reliable than trying to infer it from press coverage that may not exist for a
minor stalled bill.

**New bill found and added: Israel Land Authority Amendment (Negev/Galilee Land Allocation for
Discharged Soldiers).** A recurring private bill (traced back to 2009, most recently active
through 2025) directing free quarter-dunam plots to discharged combat-service veterans settling in
listed Negev/Galilee "National Priority Area" communities — explicitly framed by its sponsors as
"strengthening the periphery with a quality population." Confirmed via the same bill-initiator
technique to be genuinely government-aligned this time: 2021 version (defeated 42-47 at
preliminary reading) sponsored by Likud MK Yoav Kish; 2022/2023 follow-up versions (passed
preliminary readings 31-6 and 32-8) sponsored by Likud MK Nissim Vaturi. Added as a
`topic_type: "Legislative Proposal"` (never enacted, still being reintroduced) rather than
`laws.json`. Ties directly to this dataset's existing Admissions Committees Law entry — same two
regions, same "social-cultural fabric"/demographic framing, different mechanism (land grant vs.
community veto). **9 MKs get a new "For" vote** on the January 2022 vote (Smotrich, Ben-Gvir,
Katz, Hanegbi, Netanyahu, Levin, Regev, Edelstein, Maoz); **Levin and Son Har-Melech also get a
second vote** on the February 2023 follow-up versions (Levin on one, Son Har-Melech on both).

Full collision + dangling-reference check clean. 24 knesset_members (unchanged count, 10 entries
gained new vote records), 41 orgs, 52 topics (51->52), 12 laws, 36 actors unchanged. Re-embedded
and republished.

## Pre-1948 archives research + first narrative batch (2026-09-01)

Nick asked whether any of 8 named archives (Central Zionist Archives, Israel State Archives,
Labor Movement/Lavon Institute, Jabotinsky Institute, Knesset Archive/pre-state records, National
Library of Israel, Palestine Post, Center for Israel Education, Jewish Virtual Library pre-state
docs) offer machine-readable pre-state voting records/bills, mirroring the Knesset OData approach.
Real research, not a shortcut — findings, honestly negative overall:

- **Israel State Archives**: a real win — publishes a CSV file-title catalog on Israel's official
  open-data portal (`data.gov.il`, dataset `israel-state-archives-catalog`, CKAN API confirmed
  working). But it's titles only, not digitized content, and the actual download is gated behind
  Google-account login — not pursued further (account creation is Nick's to do, not something to
  push through automatically).
- **National Library of Israel**: a genuine public API (`api.nli.org.il`) covering newspaper/
  catalog search including JPress (millions of pages, Davar/Haaretz/Mandate-era press) — real
  infrastructure, but a newspaper-search API, not a legislative-records API, and self-service key
  signup is again an account Nick would need to create.
- **Central Zionist Archives** (the actual Va'ad Leumi/Asefat HaNivcharim repository): online
  finding-aid catalog exists; no API found; main site blocked automated fetches (403).
- **The Knesset Corpus** (Haifa University's own academic NLP dataset of Hebrew parliamentary
  proceedings, openly published on Hugging Face) — telling negative signal: the researchers
  explicitly excluded everything before 1992, and all pre-1948 material, citing OCR quality on
  older scans. Even a funded academic effort treats pre-state material as not machine-readable yet.
- Labor Movement/Lavon Institute and Jabotinsky Institute: catalog-only, no API.
- Palestine Post, CIE: narrative/full-text sources at the same tier as JVL/Wikipedia already used
  throughout this project, not structured vote data.

**Conclusion, agreed with Nick: pre-1948 stays narrative/secondary-sourced, same as Knessets 1-15
already are — no scraper to build here.** Began the first narrative batch, extending the existing
Yishuv/Asefat HaNivcharim/Va'ad Leumi/WZO/Jewish Agency for Palestine org entries (previously just
one bookend action_record each — founding and the 1948 handover) with real mid-period episodes:

- **World Zionist Organization**: the 20th Zionist Congress's August 1937 vote on the Peel
  Commission's partition plan — delegates rejected the Commission's specific boundaries while
  authorizing continued negotiation on the partition principle, a real distinction. Tally kept as
  a range (300-158 per Laqueur vs. 300-150 elsewhere) rather than forced to one figure.
- **Jewish Agency for Palestine**: the October 1930 Passfield White Paper (severe new immigration/
  land-purchase restrictions) → Weizmann's resignation as both WZO and Jewish Agency president in
  protest → the 13 February 1931 MacDonald Letter that effectively reversed it, dubbed the "Black
  Letter" by Arab leadership for that reason. Also added the Jewish Agency's 29 November 1947
  acceptance of the UN Partition Plan, cross-linked to the already-verified Resolution 181 entry.
- **Asefat HaNivcharim**: the 2 August 1944 election, the last before statehood — Mapai's 64/173
  seats, full party breakdown, and the Revisionist Hatzohar bloc's boycott (with fellow boycotting
  Sephardic/General Zionist B/Farmers' blocs), contrasted with the Revisionists' own 1931 17%
  second-place showing before their 1935 WZO split.

Full collision + dangling-reference check clean. Org action_record entries only (no new org/topic
counts changed) — 41 orgs, 52 topics, 24 knesset_members, 12 laws, 36 actors. Re-embedded and
republished. Next: fill remaining pre-1948 gaps (1925/1931 elections, 1939 White Paper's Yishuv-
level response, Biltmore Program adoption) opportunistically, per Nick's "both, pre-1948 first"
instruction — then resume the modern Knesset bill sweep (administrative detention, Area C, and
whatever else the keyword search turns up next).

## Resumed modern sweep: found a real enacted law that was missing (2026-09-01)

Second half of "both, pre-1948 first" — back to the modern Knesset ledger. Retried the
administrative-detention/Area C searches with alternate phrasings (still nothing under any
phrasing tried), but a broader "imprisonment/sentencing" sweep surfaced a genuinely significant
find that should have been caught in an earlier round: **Israel's actual stone-throwing minimum-
sentence law, never added to `laws.json` despite fitting squarely in Nick's original "expanded
imprisonment laws" brief.**

**Penal Law Amendment No. 120 (2015)** — real, enacted law: mandatory minimum prison sentence
(2 or 4 years, one-fifth of the applicable maximum) for stone-throwing, applied almost
exclusively to Palestinian citizens of Israel, East Jerusalem residents, and West Bank
Palestinians per Adalah's own legal analysis. Final reading passed 51-17 on 2 November 2015
(vote_id 22901, matches press exactly), after an earlier 17 November 2014 preliminary reading
57-11 (vote_id 21529). Enacted as a renewable "temporary provision," not permanent law. No
official Sefer HaChukim citation found; left `null` per standing discipline. Added to
`laws.json`.

**Found via the same search: a recurring bill to double that law's minimum sentence (2022-2025),
with a real coalition-reversal story.** Passed a preliminary reading overwhelmingly, 56-7, on 22
June 2022 — the same 24th Knesset dissolution-day session that already produced two sovereignty-
bill votes in this ledger. A near-identical re-submission was then **defeated 18-54 on 3 May
2023**, five months into the new Netanyahu government — with Netanyahu, Levin, Edelstein, and
Rothman all voting against a bill they'd voted for seven months earlier, while opposition MKs
Liberman, Sa'ar, and Elkin voted for it. Read the same way as this dataset's own Liberman/Jordan
Valley precedent: the coalition denying an opposition-adjacent bill political credit, not a
reversal on substance. Three further near-identical versions passed low-turnout preliminary
readings the same day, 12 March 2025. Added as `topic_type: "Legislative Proposal"`.

**11 MKs already in the ledger gained new vote entries**: Smotrich, Netanyahu, Regev, Hanegbi,
and Edelstein on the 2015 enactment; Smotrich, Regev, Edelstein, Rothman, Katz, and Levin on the
2022 doubling attempt; Netanyahu, Edelstein, Rothman, Levin (all "Against"), and Elkin, Liberman,
Sa'ar (all "For") on the 2023 reversal.

Full collision + dangling-reference check clean. 24 knesset_members (unchanged count, 11 entries
gained new vote records), 41 orgs, 53 topics (52->53), 13 laws (12->13), 36 actors unchanged.
Re-embedded and republished.

## Pre-1948 gaps closed: 1925/1931 elections, White Paper response, Biltmore (2026-09-01)

Nick asked to fill the remaining pre-1948 gaps flagged two rounds ago. All four closed:

- **Asefat HaNivcharim 1925 election** (6 Dec 1925, 221 seats, 57% turnout): Ahdut HaAvoda (54
  seats) and Hapoel Hatzair (30 seats) — the two labor parties that would merge into Mapai five
  years later — already the top two, ahead of the Sephardic list (19), the Revisionists' first
  appearance (Hatzohar, 15), and a long tail of smaller lists.
- **Asefat HaNivcharim 1931 election** (5 Jan 1931, 71 seats — cut from 221, reportedly to mirror
  the ancient Sanhedrin's 71 members, with 17 seats separately guaranteed to Sephardic/Yemenite
  candidates): Mapai's first election as a newly-merged party, winning 27 seats (43.45%); the
  Revisionists placed a clear second, 10 seats (16.31%) — their strongest Assembly showing, three
  years before their 1935 WZO split. This also let a small existing inaccuracy get fixed: the
  1944 election entry (added two rounds ago) had cited an approximate "17%" for the Revisionists'
  1931 showing from a secondary source; now cross-references this entry's own precise 16.31%/10
  seats instead.
- **1939 White Paper — Yishuv-level response**: added to the Jewish Agency for Palestine org
  entry (the existing White Paper topic entry only covered the document's own terms, not the
  Yishuv's reaction) — the 18 May 1939 general strike (called the same day as publication) and
  Ben-Gurion's defining wartime formula once WWII began that September: "we must help the
  [British] army as if there were no White Paper, and we must fight the White Paper as if there
  were no war." Cross-linked both directions with the existing topic entry.
- **Biltmore Program (1942)**: added to World Zionist Organization's action_record — the 6-11 May
  1942 New York conference (600 delegates, 18 countries) that first used explicit "Jewish
  Commonwealth" language rather than the deliberately vaguer Balfour-era "national home" formula,
  ratified as official WZO policy that October by the Zionist General Council in Palestine.

Full collision + dangling-reference check clean. Org action_record entries only (plus one
cross-reference fix to the existing White Paper topic and one factual tightening on the 1944
entry) — 41 orgs, 53 topics, 24 knesset_members, 13 laws, 36 actors, all counts unchanged.
Re-embedded and republished. This closes out the pre-1948 narrative batch opened two rounds ago;
further pre-1948 material (e.g. 1935 Revisionist WZO secession itself, wartime Jewish Brigade/
Haganah cooperation with Britain, the 1946 Biltmore-policy shift) would be a fresh batch, not yet
scoped or requested.

## Architecture check + Death Penalty Law + administrative detention bill (2026-09-01)

Nick: "let's get back to modern Bill sweeps," plus an aside asking what should be cleaned up
before making this available publicly.

**Architecture check (findings only, nothing actioned yet):** no git repo exists for this folder
at all — the biggest real gap given a public release is imminent; no diffable history, only the
Artifact's own version picker. The re-embed script and the collision-checker have never been
saved into the repo — both only exist as one-off Bash invocations / a session-scoped scratchpad
file, meaning no one (including a future Claude session) can rerun the publish workflow without
reconstructing them from scratch. Citation health is genuinely excellent on inspection — 265
VERIFIED citations dataset-wide, and only one citation that is *itself* bare-UNVERIFIED (a Mapai
whip-position inference in `organizations.json`, already honestly labeled as inferred); every
other "UNVERIFIED" mention found is an honest sub-detail flagged inside an otherwise-VERIFIED
citation, exactly the intended use. No public-facing About/methodology section exists yet — the
homepage's framing prose is good but doesn't explain the VERIFIED/UNVERIFIED convention to a
first-time reader who wasn't in this conversation. `data/knesset_roster_raw.json` is an
intentional raw-scrape working file, not reader-facing — no action needed there. Recommended, not
yet done: `git init` + regular commits, and a real `scripts/embed_data.py` +
`scripts/collision_check.py` checked into the repo.

**New bills found via the administrative-detention keyword retry (a different Hebrew phrasing
than tried before — 'סמכויות שעת חירום' rather than 'מעצר מנהלי') surfaced two very different, both
real, both significant finds:**

**Death Penalty for Terrorists Law, 5786-2026** — an accidental find while checking a bill's
current status, this turned out to be one of the most significant additions to the whole ledger.
Passed a final reading 62-48-1 on 30 March 2026 (matches the scrape exactly), after 8 prior failed
attempts stretching back to 2015. Sponsored by Otzma Yehudit MK Limor Son Har-Melech (already in
this ledger). Makes death by hanging mandatory for murder committed "with the aim of denying the
existence of the State of Israel" — a standard the law's own critics, and the UN Committee on the
Elimination of Racial Discrimination formally, describe as worded to exclude Jewish perpetrators
while applying de facto only to Palestinians. Added to `laws.json` (a real enacted law) with the
CERD finding and the striking conviction-rate disparity (99.74% for Palestinians in military
courts vs. ~3% for Israelis tried for West Bank crimes, 2005-2024) recorded in its `land_impact`
field. **10 MKs get a new vote**: Rothman, Ben-Gvir, Elkin, Katz, Netanyahu, Levin, Liberman
(all "For"), Lapid and Gantz (both "Against," a genuine mainstream-opposition contrast point).

**Emergency Powers (Detentions) Law Amendment (Administrative Detention Limit for Israeli
Citizens), 2024** — the opposite kind of find: a bill that *narrows* a punitive power rather than
expanding it, specifically and only for Israeli citizens. Sponsored by Rothman (confirmed directly
via the Knesset's own `KNS_BillInitiator` API record, not press alone), it would bar administrative
detention against Israeli citizens except for a defined terror-organization-membership list, while
leaving the same power fully intact against West Bank Palestinians — Haaretz's own headline called
it plainly: "Israeli Ministers Approve Law That Would Reserve Administrative Detention for
non-Jews." Passed a preliminary reading 54-51 on 3 July 2024 over public Shin Bet objections. Added
as a `topic_type: "Legislative Proposal"` (not yet confirmed to have completed all three readings;
a related but distinct May 2026 executive action by Defense Minister Katz ending administrative
detention of Israeli citizens in the West Bank was found and explicitly not conflated with this
bill's own legislative status). **10 MKs get a new vote**: Rothman (sponsor), Katz, Levin,
Edelstein, Son Har-Melech (all "For"); Elkin, Liberman, Lapid, Sa'ar, Gantz (all "Against") — a
genuine, non-simple coalition/opposition split (Elkin and Liberman broke with the government line
here despite backing it on the death penalty law).

Full collision + dangling-reference check clean. 24 knesset_members (unchanged count, 12 entries
gained 20 new vote records total across both bills), 41 orgs, 54 topics (53->54), 14 laws
(13->14), 36 actors unchanged. Re-embedded and republished — content verified landed correctly via
direct grep of the published HTML rather than the usual local browser check, since the browser
preview tool was intermittently failing to open the local file this round (unrelated to the data
itself; JSON validation and the collision check both passed cleanly beforehand).

## Citizenship Law renewal vote + the 2020 Outposts Law finally chased down (2026-09-01)

Nick's message repeated (likely a client hiccup) — continued the same "keep going" bill sweep.

**Citizenship and Entry into Israel Law — concrete renewal-vote evidence added.** The existing
law entry already asserted "repeatedly renewed... permanent in practice" without a specific vote
behind it. Added one: the 10 March 2025 government request to extend the law by order passed
48-9-1 (vote_id 43270, `ForOptionDesc` confirmed via the Knesset API as literally "approve the
secondary legislation," i.e. the renewal itself). 3 MKs gained a vote (Rothman, Elkin, Levin, all
"For") — Elkin's vote is notable as cross-coalition/opposition-adjacent support for a law usually
framed in security terms.

**Finally ran down the 2020 "Outposts Law" flagged three rounds ago and repeatedly missed by
keyword search.** Found it by searching press for the bill's English description first, then
matching the December 2020 date window directly against the vote titles rather than guessing
Hebrew phrasing — a more reliable method worth remembering for future stubborn leads. Real title:
"Communities and Neighborhoods in Regularization Processes Bill" — grants government financial
support and Israeli infrastructure connection (water/electricity/postal) to West Bank outposts
already undergoing regularization, distinct in mechanism from the already-covered 2017
Regularization Law (that one addressed retroactive legal status on private Palestinian land; this
one addresses ongoing material support regardless of land-tenure status). Passed a vote toward
second/third readings 60-40 on 16 December 2020 (press reported this stage 59-39, a minor
unreconciled variance). **15 co-sponsors confirmed via the Knesset's own `KNS_BillInitiator` API**,
including Smotrich, Shaked, Halevy, and Haim Katz — matching press exactly. This bill's own final
enactment status was not confirmed via live search this pass; added as a `topic_type:
"Legislative Proposal"` rather than assumed enacted. **10 MKs get a new vote**: Smotrich (sponsor),
Shaked (co-sponsor), Liberman, Elkin, Hanegbi, Levin, Regev, Edelstein, Bennett (all "For");
Lapid (the sole "Against" among this dataset's tracked MKs on an otherwise broadly-backed bill).

Full collision + dangling-reference check clean. 24 knesset_members (unchanged count, 13 entries
gained 13 new vote records), 41 orgs, 55 topics (54->55), 14 laws unchanged (one citation
enriched), 36 actors unchanged. Re-embedded and republished — browser preview tool was still
failing to open the local file this round (second round running); verified the publish via direct
grep of the published HTML for new content strings, same workaround as last round, after JSON
validation and the collision check both passed cleanly.

## Nakba Law + Boycott Law, 2011 (2026-09-01)

Nick: "new bill categories then the architecture." A fresh keyword sweep for two well-known 2011
laws not yet in the ledger, both found cleanly by searching for their real official titles first.

**Nakba Law — Budget Foundations Law (Amendment No. 40), 5771-2011.** Passed 37-25 late on 22/23
March 2011, sponsored by Yisrael Beiteinu MK Alex Miller with three co-sponsors (David Rotem,
Fania Kirshenbaum, Hamad Amar — all confirmed via the Knesset's own `KNS_BillInitiator` API,
matching press exactly). Authorizes the Finance Minister to withhold state funding from any
government-funded institution that marks Israel's Independence Day as a day of mourning — a
direct legislative attempt to suppress institutional commemoration of the same 1948 displacement
this dataset already documents via its own Nakba and 1948 Arab-Israeli War topic entries, now
cross-linkable. Added to `laws.json`. **5 MKs get a new vote**: Elkin, Levin, Hotovely, Edelstein,
Liberman (all "For").

**Boycott Law — Law for Prevention of Damage to the State of Israel through Boycott, 5771-2011.**
Passed 47-38 on 11 July 2011, sponsored by a 19-MK group (confirmed via the same API technique) —
including Elkin, Levin, Katz, and Hotovely, all already in this ledger. Creates civil liability,
without needing to prove actual damages, for anyone calling for a boycott of Israel — and its own
text expressly extends that liability to boycotts of West Bank settlements specifically, the
clause that puts it in this dataset's scope. An initial draft's criminal penalties and
citizens-only scope were both stripped before final passage. **6 MKs get a new vote** (some
overlapping with the Nakba Law batch): Elkin, Levin, Katz, Regev, Hotovely, Edelstein (all "For").

Full collision + dangling-reference check clean. 24 knesset_members (unchanged count, 7 entries
gained 11 new vote records total across both laws), 41 orgs, 55 topics, 16 laws (14->16), 36
actors unchanged. Re-embedded and republished — browser preview tool still failing to open the
local file (third round running); verified via direct grep of the published HTML for new content
strings, after JSON validation and the collision check both passed cleanly, same workaround as
the prior two rounds.

Moving to the architecture cleanup Nick asked about next.

## Architecture cleanup actioned (2026-09-01)

Nick: "let's do the architecture." Actioned the three findings flagged two rounds ago, all before
any public sharing:

**Git repo initialized.** `git init` in the project folder, real global identity already
configured (no setup needed). Added a `.gitignore` excluding `data/knesset_votes.sqlite3` — at
234MB it's both too large for a normal git workflow (GitHub blocks pushes over 100MB) and was
never meant to be distributed itself; it's a regenerable research artifact (`scripts/
knesset_scraper.py` rebuilds it from the Knesset's own public API), not part of what's meant to be
public. Everything else — all six `data/*.json` files, `SCOPE.md`, `SCHEMA.md`, `wiki-prototype.html`,
the map prototype HTMLs, the two PDF primary sources, and all five scripts — is now in an initial
commit (21 files, root commit `d5569cf`).

**Both working scripts saved into the repo for real**, ending the "only exists as one-off Bash
this session" problem: `scripts/embed_data.py` (the re-embed step, previously always retyped
inline) and `scripts/collision_check.py` (moved out of the session-scoped scratchpad it's lived
in all along). Both tested working before commit — `embed_data.py` correctly re-synced all six
files (36/41/24/6/16/55 entries) and `collision_check.py` ran clean. Either can now be rerun by
any future session (or another contributor) without reconstructing them from a transcript.

**Added a real About/methodology page** (`#/about`, linked from the header and the homepage hero)
— the wiki had good framing prose but nothing explaining the VERIFIED/UNVERIFIED convention, where
the Knesset ledger's data comes from, or the living-persons discipline to a reader who wasn't in
any of these research sessions. Covers: what the site is, how a citation works (with the Land
Acquisition/Absentees' Property Law wrong-guess story as a concrete example of why the discipline
exists), where pre-1948 vs. post-2003 material each comes from and why they're sourced
differently, the living-persons standard, and an honest "not exhaustive, not finished" closer.
Verified via `node --check` on the extracted inline script (JS syntax clean) since the browser
preview tool remained unable to open the local file this round too (fourth round running) —
JSON/collision checks aren't relevant here since no data file changed, just the HTML/JS directly.

Re-embedded (via the new script) and republished before the git commit, so the initial commit
captures the working, published state. Not yet done, and worth flagging for whenever Nick's ready
to actually make the repo public: no remote configured yet (this is a local-only repository so
far — pushing to GitHub or elsewhere is a separate, explicit step Nick should decide on, not
something to do unprompted).

## Voice profile set up + new `personal_context` field, Netanyahu example (2026-09-02)

Two real asks in one round: de-AI the site's own framing prose, and start giving Actors/MKs a
bit of biographical color beyond their land record.

**Set up a `my-writing-style` voice profile.** Nick pasted 8 real emails (Scout Adventure Team
booking, his dad, an order-cancellation to a retailer, a museum membership request, friends,
South East Water, a pans-discount negotiation, a friend re: coffee) — one register (email), one
audience, honestly flagged as below the skill's ~10-per-surface floor rather than presented as a
deep read. Real, checkable traits came out of it: warm/playful greetings even to strangers,
leads with owning any friction before the ask, narrates his own reasoning on the page rather than
just stating conclusions, notices the person on the other end, and — the one that mattered most
for this project's own writing — **almost never uses an em-dash, semicolon, or bullet list**,
which is close to the opposite of how this project's own SCOPE.md/citation prose has been written
all along. Saved to `~/.claude/skills/my-writing-style/SKILL.md` with a `~/.claude/CLAUDE.md`
pointer so it loads automatically in future sessions.

**Rewrote the About page and homepage intro in that voice** — first person, no em-dashes, no
semicolons, no bullet list for the VERIFIED/UNVERIFIED explanation (converted to two short
paragraphs instead). Content and citations unchanged, just the framing prose Nick had
screenshotted as reading too AI-generated.

**New schema field: `personal_context`**, added to both `historical_actors.json` and
`knesset_members.json` (documented in SCHEMA.md). Deliberately kept separate from
`key_land_actions`/`legislative_and_action_record` — this dataset's core subject stays land and
dispossession, and `personal_context` is explicitly the "rest of the person" field: family,
military service, a major unrelated event, or — for a living person — an active legal matter.
Same living-persons discipline as everywhere else: real citations, and for an ongoing legal
matter specifically, every charge stated as alleged until there's an actual verdict.

**Netanyahu given as the concrete first example, two entries:** his brother Yonatan "Yoni"
Netanyahu's death commanding the Sayeret Matkal assault force in the July 1976 Entebbe raid (the
operation was renamed Operation Yonatan in his memory — he was the raid's sole Israeli fatality),
and his own ongoing corruption trial (Cases 1000/2000/4000, indicted November 2019 as the first
sitting Israeli PM ever criminally charged, still without a verdict as of this entry — his own
testimony wrapped in June 2026 after 98 hearings, and as of July 2026 judges have twice suggested
the prosecution reconsider the Case 4000 bribery charge, with nothing formally dropped or decided
yet). Wired `personal_context` into both `renderActor()` and `renderMK()` as a new "Beyond the
ledger" section.

Full collision + dangling-reference check clean — using the newly-committed `scripts/
collision_check.py` and `scripts/embed_data.py` for the first time as real repo tools rather than
retyped inline, both worked end to end. 24 knesset_members (unchanged count, Netanyahu gained 2
personal_context entries), all other files unchanged. Re-embedded, JS syntax verified via
`node --check` (browser preview tool still down, 6th round running), republished, and committed.

**Not yet decided:** whether `personal_context` gets rolled out further (other Actors/MKs with a
similarly notable personal story) is Nick's call — Netanyahu was the explicit example given, not
a signal to sweep the whole dataset. Also not yet actioned: pushing the local repo to the GitHub
remote Nick set up (`github.com/nickrolle-rgb/TheDispositionPapers`) — he said he's happy to keep
building first, so this stays a local-only repo until he says go.

## Personal-life sweep: all 60 people done (2026-09-02)

Nick: "let's expand Personal Life to all Actors and MKs!" Full sweep, in six checkpointed
batches (20 actors, then the remaining 16, then MKs in batches of 4/4/8/3/1), each validated,
collision-checked, re-embedded, and published before moving on — same discipline as every other
batch in this project, just at real scale (60 people, ~60 research passes).

**All 36 historical actors and all 24 Knesset Members now carry a real `personal_context`
entry.** A few things worth recording from doing this at scale:

- **Real cross-links surfaced that weren't previously connected in this dataset**, found only
  because the research touched every person in the same sitting: Yehoshua Hankin's wife Olga was
  Israel Belkind's sister (both already separate entries); Yisrael and Manya Shochat were married
  (also both separate entries); Ber Borochov is buried at Kibbutz Kinneret alongside Moses Hess;
  Tzachi Hanegbi's parents were both Lehi underground fighters (his mother Geula Cohen a
  well-known Lehi radio announcer and later MK herself), directly touching this dataset's own
  Lehi org profile. None of these were flagged before because no single research pass had reason
  to check.
- **Living-persons discipline held under real pressure.** Several entries touch genuinely
  sensitive territory — Ben Gvir's Irgun-veteran mother, Smotrich's own family home's disputed
  building-plan status, Son Har-Melech's first husband's murder and her own wounding in the same
  2003 attack, Gantz's wife's Alzheimer's diagnosis, Maoz's wedding officiant's pointedly opposite
  politics — each kept to documented fact with a real citation, no editorializing added.
- **Not every entry warranted two items the way Netanyahu's did** — most people got one solid,
  well-sourced personal_context entry rather than being padded to match Netanyahu's depth; some
  (Katz, Halevy) are genuinely thin in what's publicly documented about their personal lives, and
  the entries reflect that honestly rather than manufacturing color that isn't there.

Full collision + dangling-reference check clean at every checkpoint. Final state: 36 actors, 24
knesset_members (all with personal_context), 41 orgs, 55 topics, 16 laws — unchanged elsewhere.
Six publishes, six commits. Browser preview tool remained down the entire sweep; every publish
verified via `node --check` on the extracted script plus JSON/collision checks, the workaround
established two rounds ago.

### Betar added as a standalone org (2026-09-02)

Nick asked whether Betar (the Revisionist youth movement) deserved its own listing. It was
previously only present as a string ("Betar (founder)" in Jabotinsky's affiliations, a mention in
Begin's personal_context) — confirmed via grep before starting, no standalone entry existed. Given
it directly trained the founders of Irgun, Lehi, Herut and Likud — all already-covered orgs in this
dataset — this was a real, well-justified gap, not scope creep.

Added `betar` to `data/organizations.json` (new `org_type: "Youth Movement"`, already anticipated
in SCHEMA.md's enum but unused until now — documented in SCHEMA.md with a dated footnote matching
the file's existing convention). Three action_record entries: the 1923 Riga founding, the 1935
Krakow conference (Ha-Neder oath, Hadar code, the Civitavecchia naval academy that fed Haganah/
Irgun/Lehi), and its lineage into Herut/Likud via Begin and Shamir. Still active today (no
`dissolution_date`/`merged_into`, same null pattern as Likud) — the "still active, shares premises
with Likud" claim is flagged lower-confidence since it traces to a single organization's own
account (Betar USA), everything else independently corroborated across 2+ sources.

Also added "Betar (Commander, Poland, 1938-39)" to Begin's `primary_affiliations` and "Betar
(joined 1929, age 14)" to Shamir's, matching the pattern Jabotinsky's entry already used — both
dates newly verified via live search this pass, not previously in the dataset.

Collision check clean, one publish, one commit.

### First push to GitHub (2026-09-02)

Nick asked to publish to GitHub and go live on Vercel. Pushed the local repo (10 commits deep,
git-init'd earlier this session) to `https://github.com/nickrolle-rgb/TheDispositionPapers` —
confirmed via `gh repo view` the repo already existed (Nick created it), was empty, and correctly
owned by his account before pushing; `gh auth status` showed his own CLI session already
authenticated, so this used his existing login rather than any new auth flow. Repo is small and
clean (2.7MB tracked, `knesset_votes.sqlite3` correctly gitignored). Flagged to Nick: the repo name
he typed is "TheDispositionPapers" (Disposition, not Dispossession) — likely a typo, left as-is
since renaming a GitHub repo is his call.

Added `vercel.json` rewriting `/` → `/wiki-prototype.html` only (main deliverable isn't named
`index.html`; scoped narrowly so the other standalone prototype HTML files and PDFs in the repo
root stay reachable at their own paths). Repo is now Vercel-deployment-ready. The actual
GitHub-repo-to-Vercel connection step needs Nick's own vercel.com login — not done here, per the
standing rule against completing OAuth/account-linking on his behalf.

## Open

- Actor roster, organizations, and MK calibration sets still awaiting Nick's review.
- CIJA (Canada) — closed permanently, no further automated lookup (see above).
- Knesset scraper: full v4 vote_results pull in progress (~1.95M rows, resumed twice now after
  unexpected background-process stops — checkpointing is doing its job).

## Party/faction data + land-vote research tool (2026-08-31)

Realized the transform into `knesset_members.json` was under-specified two ways, fixed both
before writing it:

1. **Party affiliation wasn't captured at all.** `KNS_PersonToPosition` filtered to
   `PositionID=43` (Member of Knesset) never carries `FactionID`/`FactionName` — those live on
   a *separate* record type, `PositionID=54` ("חבר/ת סיעה", Faction Member), confirmed live by
   checking one MK's full position history. Added `scrape_party_membership()` to the scraper
   (new `mk_party_membership` table) — 4,517 records, e.g. Netanyahu's full party-list history
   across Knessets 12-25 including the electoral-alliance name variants. Small/fast, ran
   alongside the big pull with no lock conflicts.
2. **A blind 1:1 dump of ~2M vote rows into the curated JSON was the wrong plan.** Almost all
   Knesset votes have nothing to do with land policy, and the schema's `land_impact` fields
   need a real citation per the project's own discipline — auto-filling ~2M of them isn't
   possible or desirable. Built `scripts/find_land_votes.py` instead: keyword-searches
   `votes.title_he` across themed Hebrew term groups (land/land-law, expropriation, absentee
   property, settlement, planning & building, annexation/border, evacuation/demolition,
   JNF/Israel Lands Authority) and returns candidate votes for review. Tested against what's
   scraped so far: **720 distinct candidate votes**, including the 2005 Gaza disengagement
   plan roll calls, the 2006-2007 JNF/KKL land-transfer controversy, the 2021 West Bank
   sovereignty bill, and absentee-property amendments — genuinely on-target hits, not noise.
   Also supports `--mk <person_id>` to pull one person's land-relevant vote history directly.
   This is the real pipeline going forward: search → human (or Claude) reviews candidates →
   promote the real ones into `knesset_members.json` with an actual citation, same discipline
   as the Kaplan/Eshkol calibration entries.
- Scrolly map: stage-sync rough edge (see above); Peel Commission's proposed partition line
  and 1920s land-purchase parcels have no real boundary data — would need a historical GIS
  source (not found yet) to depict spatially rather than as markers only.
- `israel-defense-forces` and `israeli-labor-party` are referenced as lineage targets but have
  no org record yet (IDF may be out of scope entirely — it's a national army, not a
  party/militia). `Gahal` (1965 Herut-Liberal alliance) also referenced but not profiled.
- `political_alignment` and `category`/`land_impact` vocab in schema 2 are Nick-specified
  free text for now — no controlled-vocabulary lock requested, unlike Money Tracker.
- Repo layout beyond `data/` (storage format — flat JSON vs. sqlite/Postgres — not decided).

## Repo renamed, Vercel live (2026-09-02)

GitHub repo renamed `TheDispositionPapers` → `TheDispossessionPapers` (Nick asked directly; done
via `gh repo rename`, local remote URL updated to match, pushed clean). Vercel is live at
https://the-disposition-papers.vercel.app/ — Nick connected it himself.

## Betar re-sourced + first real pass on the 700-vote backlog (2026-09-02)

Nick asked to (1) source the Betar "shares premises with Likud" claim properly, (2) start
working the ~700-candidate land-vote backlog `find_land_votes.py` surfaces, and (3) chase the
2020 outposts funding bill specifically.

**2020 outposts bill: already done.** Checked before starting — it's the existing
`communities-neighborhoods-regularization-bill-2020` topic entry (added earlier this session,
before this round), fully cited with all 15 co-sponsors and every MK's vote already recorded. No
new work needed; told Nick directly rather than silently re-adding it.

**Betar sourcing:** found Wikipedia's own Metzudat Ze'ev article — genuinely independent of
Betar's own accounts, confirms the shared-building claim with real construction history (built
1936-63 on the site of the 1930s Revisionist/Betar/Irgun HQ shack; today also houses the
Jabotinsky Institute/Museum, Irgun Museum, Partisans and Fighters Museum). Betar org entry's
citation upgraded from single-source to two independently-corroborating sources.

**Vote backlog — real methodology, not a blind sweep:** re-ran `find_land_votes.py`'s full
keyword search (720 raw hits), excluded the 12 already-promoted vote_ids and 9 matrimonial-
property false positives (Hebrew "הפקעה" also means financial-rights forfeiture in divorce law —
unrelated to land), leaving 699 real candidates. Bucketed by title pattern: 476 genuine bill-track
rows (246 unique bills after deduping multiple readings), 75 agenda motions, 49 no-confidence
motions, 98 other, 1 ILA decision. **Read all 246 unique bill titles by hand** — the large
majority are generic property/tax-law technical amendments (elevator installation rules, transfer
tax brackets, earthquake reinforcement, mediator licensing) with no real connection to this
dataset's subject; screened out as noise rather than promoted.

**4 genuinely on-topic finds, live-search verified, all added:**
- **UNRWA property/utilities law (2025)** — new `laws.json` entry. First reading 19 Nov 2025
  (28-8 per press; scrape shows a lower-turnout 4-2 attendance tally, variance flagged not
  reconciled), final third reading 29 Dec 2025, 59-7. Seizes two named UNRWA office properties in
  Jerusalem (Ma'alot Dafna, Kafr Aqab) without legal process, on top of a utilities cutoff. Also
  linked to Liberman's own vote record (For, first reading).
- **WZO Settlement Division land-management bill (2018)** — new `topics.json` Legislative
  Proposal. Would hand ~400,000-500,000 dunams (~60% of West Bank state land) of ongoing Area C
  land-management authority to the WZO's Settlement Division rather than the Civil
  Administration. Passed first reading 48-44 (13 June 2018), then held for a possible Cabinet-
  decision alternative — final status unresolved, kept as proposal not enacted law.
- **Jordan Valley Sovereignty Bill — extended into a two-attempt trajectory.** Found a second,
  distinct attempt (22 Jan 2025, defeated 32-56) beyond the already-covered 2023 one (65-14) —
  same underlying policy, opposite coalition/opposition alignment: Ben Gvir's Otzma Yehudit,
  freshly out of government, voted for it this time; the government voted it down on procedural/
  timing grounds rather than substance.
- **Elimination of Discrimination in Land Purchase Bill (2023-2025)** — new `topics.json`
  Legislative Proposal. Repeals the 1953 Jordanian law barring non-Jordanians from buying West
  Bank land — the last formal limit on unrestricted settler land purchase. Two versions passed
  preliminary reading 57-33/58-33 (29 Jan 2025); only committee-approved as of the most recent
  check (26 Nov 2025), not yet enacted — kept honestly as still-pending, not assumed passed.

**One real dead end, documented not silently dropped:** a 2012 Negev Bedouin demolition-orders
bill (Planning and Building Law amendment) looked promising but its only floor vote (31-1) is a
bare committee-referral, the exact "check `vote_subject_he` before treating a vote as
substantive" trap flagged two rounds ago — no confirmed record of it reaching a real passage vote,
so not added. Same discipline held under a second real test.

**Backlog remaining, explicitly not yet touched:** the 75 agenda-motion and 49 no-confidence
buckets, and the 98 "other" bucket, haven't been reviewed at all — this round only covered the
476-row/246-unique "bill" bucket. Continuing on request.

24 knesset_members (1 gained a vote), 42 orgs (1 citation upgraded), 17 laws (16→17), 57 topics
(55→57, 1 extended not new), 36 actors. Collision check clean, one publish, one commit.

## Vote backlog, remaining buckets: no-confidence, agenda-motion, other (2026-09-02)

Continued the backlog sweep, covering the three buckets not yet touched: no-confidence motions
(46 unique), agenda motions (68 unique), and everything else (74 unique) — 188 titles read by
hand. Confirmed the standing lesson holds at scale: the overwhelming majority of these are
symbolic political theater — no-confidence motions fail predictably along coalition/opposition
lines regardless of the underlying policy's merits, and agenda motions are votes on whether to
*discuss* a topic, not on the topic itself. Did not force-promote any of these as individual
ledger entries; instead scanned all three buckets for underlying real, undocumented land actions
the motions were reacting to, matching the method that already worked for the UNRWA/WZO/Jordan
Valley finds last round.

**3 real finds, all live-search verified and added:**
- **Negev Bedouin Land Claims Settlement Plan (2026)** — new `topics.json` entry. An Israel Land
  Authority administrative plan under Minister Amichai Chikli's "Negev reform," published 16
  April 2026: ~3,200 Bedouin ownership claims from the early 1970s, claimants required to
  evacuate and relocate to a government-provided plot within 10 months for a cash grant. A
  genuine successor in substance to the withdrawn 2013 Prawer-Begin Plan, repackaged as an
  incentive-based administrative program rather than one Knesset bill — the follow-on
  no-confidence motion (8 June 2026, defeated along coalition lines) is what surfaced it.
- **Al-Araqib** — new `topics.json` Geographic Region entry, and a real gap: the single
  most-repeated demolition case in the whole subject area (demolished 238+ times since 27 July
  2010, roughly monthly) had no entry at all despite being one of the most-cited case studies in
  this exact literature. Surfaced via a 2010 agenda motion on "unrecognized villages including
  Al-Araqib," not a bill.
- **Symbolic sovereignty motion, July 2025** — new `topics.json` entry, distinct from the
  already-covered binding sovereignty bills. A non-binding "sense of the Knesset" resolution
  passed 71-13 on 23 July 2025 (Ofir Katz's version, beating four rejected opposition
  alternatives) — a far wider margin than the actual bills' single-vote/single-digit passages,
  worth keeping as its own entry precisely because it shows the gap between rhetorical consensus
  and legislative willingness.

**Flagged, not chased this round** (real leads, lower priority): a 2004 High Court ruling that a
soldier-preference land-purchase tender discriminated against Arab citizens; a 2019 report that
Finance Ministry administrative planning/building fines fell disproportionately on Arab
communities. Both are court/executive-branch actions, not Knesset votes — would need their own
research pass, not mined from the vote corpus directly.

**Vote backlog is now substantively closed for this methodology.** All four buckets
(bill/no-confidence/agenda-motion/other) have been read in full at least once. Real further
progress from here would mean chasing the two flagged leads above, or a fresh keyword sweep on
terms not yet tried (the existing 8 keyword groups are unlikely to surface much more).

36 actors, 24 knesset_members, 42 orgs, 17 laws, 60 topics (57→60). Collision check clean, one
publish, one commit.

## The two flagged leads, chased down (2026-09-03)

**Lead 1 (2004 HCJ soldier-preference land-tender ruling) turned out messier than the vote title
implied — chased it honestly rather than forcing a clean story.** The 2004 Knesset motion referenced
an HCJ finding that a soldier-preference discount in land tenders discriminates against Arab
citizens; live research found this sits inside a tangle of related-but-distinct Adalah petitions
(a 2004 land-lease-discount petition the Attorney General opposed, a separate December 2005
mortgage-benefit petition that a three-judge panel actually *rejected* in December 2006). No
confirmed final ruling on the specific 2004 land-tender petition was found. Rather than either
dropping the lead or inventing a resolution, kept chasing turned up the real, foundational case
underneath all of it: **Ka'adan v. Israel Lands Administration** (filed 1995, ruled 8 March 2000)
— the landmark Supreme Court decision that public land can't be allocated through a Jewish-only
cooperative-society mechanism, "what the State cannot do directly, it cannot do indirectly." A
genuinely significant gap: one of the most-cited land-discrimination rulings in the whole
literature, and this dataset had never had an entry for it. New `topics.json` Historical Event
entry, with the narrower 2004-2006 soldier-preference thread documented honestly inside its own
citation rather than conflated with Kaadan. Also flagged: the Admissions Committees Law (2011,
already in this dataset) is widely read as the Knesset's legislative answer to Kaadan — reinstating
by statute the same discretion the Court had just ruled out, dressed as a "social-cultural fitness"
criterion.

**Lead 2 (2019 report on discriminatory planning fines) resolved cleanly** — it's a real
enrichment to the already-existing Kaminitz Law (2017) entry, not a separate topic. Found Ayelet
Shaked's own November 2019 on-record admission that "the aim was to tighten enforcement on
illegal construction, especially in the Arab sector," and the follow-on: Attorney General Avichai
Mandelblit's office announced a "change in enforcement" on 12 November 2020 (heaviest fines
unenforced for two years, pre-2018 houses overlooked) after sustained backlash — Arab leaders
called it a de facto freeze, the AG's office called it a policy shift. Both added to the existing
`kaminitz-law-2017` entry's summary and citation rather than creating a duplicate.

36 actors, 24 knesset_members, 42 orgs, 17 laws (1 enriched), 61 topics (60→61). Collision check
clean, one publish, one commit.

## Samson Option added (2026-09-03)

Nick asked for a listing on the Samson Option — Israel's undeclared nuclear-deterrence doctrine.
Confirmed via grep it didn't exist yet, then researched properly: new `topics.json` entry
(`topic_type: "Historical Phenomenon"`) covering the 3 October 1957 France-Israel agreement, the
Dimona reactor's 1958 construction under heavy secrecy (the Latin-American-desalination-plant
cover story), Ben-Gurion's 21 December 1960 Knesset statement downplaying it as a research
reactor after US discovery via U-2 overflights, and the term's mid-1960s coining among Ben-Gurion/
Eshkol/Dayan/Peres (per Hersh and Avner Cohen's research specifically — attributed rather than
independently verified, given the deliberate secrecy around the subject) through to its public
exposure via Seymour Hersh's 1991 book. Linked to Ben-Gurion and Dayan (already profiled); Eshkol
already profiled as an MK, referenced in prose; Peres named but not linked — not currently in this
dataset as his own entry. Outside the land-dispossession core thesis but consistent with the
project's established practice of covering broader ideological/foreign-policy topics (Iron Wall
doctrine, Muscular Judaism) alongside it.

36 actors, 24 knesset_members, 42 orgs, 17 laws, 62 topics (61→62). Collision check clean, one
publish, one commit.

## Defensible Borders Doctrine added (2026-09-03)

Nick asked for "a doctrine element that explains the expansion strategy or reluctance to forfeit
territory" — researched to find the actual named doctrine rather than guessing: **Defensible
Borders**, the real, formally-named post-1967 Israeli security doctrine (distinct from Iron Wall,
which is pre-state and about the path to founding, not post-1967 withdrawal reluctance). New
`topics.json` entry covering the strategic rationale (Golan overlooking the Hula Valley, the West
Bank's narrow waist, Gaza's proximity to population centers), its architects (Allon, Dayan, Rabin,
Sharon — all but Rabin already profiled here), and Abba Eban's November 1969 "Auschwitz borders"
quote — included with the honest, often-omitted fuller context: the same interview also had Eban
saying Israel "could not and should not retain the occupied territories." Cross-referenced against
the already-covered Resolution 242 ("land for peace") and Allon Plan entries as the doctrine's
counterweight and first concrete territorial expression, respectively. Extended to the present with
its post-October-2023 reinvocation (Gaza/Lebanon/Golan buffer zones). Abba Eban and Yitzhak Rabin
named in prose but not linked — neither is currently profiled as their own entry in this dataset.

36 actors, 24 knesset_members, 42 orgs, 17 laws, 63 topics (62→63). Collision check clean, one
publish, one commit.

## UN Resolution renaming + "International Perspective" section confirmed (2026-09-03)

Nick asked to prefix all "Resolution N" topic names with "UN" — done across all 10 UN Resolution
entries (181, 194, 242, 273, 303, 338, 465, 478, 497, 3379). Kept the bare "Resolution N" form as
an alias on each (rather than dropping it) after checking: it's used constantly in running prose
elsewhere in the dataset ("...reaffirming Resolution 242 in all its parts"), and dropping it would
have silently broken autolinking on every one of those mentions — the same class of mistake as the
earlier "Yishuv" lowercase-alias bug, caught before publishing this time by actually grepping for
existing bare mentions first.

Nick confirmed the proposed "International Perspective" section (UN Resolutions + campaigns not
being followed, kept separate from Actors/Orgs/MKs/Laws in both the text index and the network
view) — not built yet, next up on request.

## Org aliases field added; real cross-link gaps found and fixed (2026-09-03)

Nick asked whether "JNF" is aliased to Jewish National Fund (it wasn't — organizations.json had
no `aliases` field at all, unlike topics.json) and to use it as a template to link Yosef Weitz,
who was flagged as unaffiliated/unlinked despite his own `primary_affiliations` already reading
"Jewish National Fund (Head, Lands Department)."

Added a proper `aliases` field to the org schema (documented in SCHEMA.md), wired into both
`scripts/collision_check.py` and the wiki's own JS `nameIndex` builder alongside the existing
`MANUAL_ALIASES` dict. Jewish National Fund now carries `["JNF", "Keren Kayemeth LeIsrael",
"KKL"]`.

Used the same "documented in prose but not structurally linked" pattern to sweep the rest of the
dataset rather than fixing only Weitz: found 4 more real gaps (Arthur Ruppin → Jewish Agency for
Palestine, Menachem Ussishkin and Zvi Hermann Schapira → World Zionist Organization, Yitzhak
Shamir → Herut) — all cases where an actor's own `primary_affiliations` text already named the
org but the org's `notable_members` array didn't reciprocate. Fixed all 5 (including Weitz).

Same sweep applied to topics: two topics (British Mandate, Balfour Declaration) discussed the
League of Nations in their own prose but weren't linked to the `league-of-nations` org via
`related_org_ids` — fixed both. Surfaced while investigating Nick's request to reveal Mandate-era
topics under League of Nations in the network view.

36 actors, 24 knesset_members, 42 orgs (5 gained notable_members, 1 gained aliases), 17 laws, 63
topics (2 gained related_org_ids). Collision check clean, one publish, one commit.

## Network view v3: alignment reasoning fixed, topics reveal on zoom, roles clarified (2026-09-03)

Nick's follow-up round on the network prototype, all real fixes not just polish:

**Legend bug**: the shape-legend icons were rendering at full size instead of 10px — a CSS
specificity collision (`.graph-wrap svg { width: 100%; height: 100% }` was beating the intended
`.shico` rule). Fixed with an explicit `svg.shico` selector; legend also compacted into one row
and simplified per Nick's request (Actor+MK merged into a single "Person" circle, Law's triangle
given rounded corners via `stroke-linejoin: round` to match the rounded language everything else
uses).

**Alignment classification, reasoned properly this time.** Nick correctly flagged Kadima not
sharing Likud's colour as wrong, and asked for genuine institutions/offices (that "could change
hands") to stay visually distinct regardless. Rebuilt the classifier in three passes: (1) org_type
membership in a defined institutional set — Government Office, Legislative Body, Sovereign State,
National Military, International Body, etc. — always wins, never overridden by ideology text or
lineage (this is what keeps Prime Minister/President/Knesset/IDF/UN bodies grey no matter who
holds them); (2) direct ideology-keyword match for everything else; (3) lineage propagation for
orgs whose own ideology tag doesn't keyword-match but whose predecessor/successor does — this is
what fixes Kadima (tagged merely "Centrist," but lineage-linked to Likud) without hardcoding it.
Anything still unresolved after all three passes (Hovevei Zion, the South Lebanon Army) now falls
to honest "no data" rather than being folded into "institutional" as a catch-all.

**Topics now reveal on zoom, same mechanism as laws.** Added all 63 topics.json entries as a 5th
node kind (hexagon shape), hidden until a connected node is selected — wired from each topic's
own `related_actor_ids`/`related_org_ids` fields, so UN Resolutions surface under United Nations
General Assembly/Security Council and Mandate-era topics surface under League of Nations, exactly
matching how laws surface under their sponsors. 59/63 topics already carry real connections; no
data invented for this.

**Organic layout**: isolated nodes were lining up in a visible row along the canvas edge — a hard
position clamp, not a real layout choice. Replaced with a soft push-back force plus a faint
persistent jitter, so untethered nodes settle into a scatter instead of a grid.

**PM/President roles clarified**: Nick asked for text explaining what these offices actually do.
Prime Minister's entry gained a lead sentence on the parliamentary-confidence mechanism (appointed
by coalition, not direct vote; removable by no-confidence) and why cabinet decisions through this
office — not Knesset legislation — are what actually drives the post-1967 settlement record this
dataset tracks. President's entry gained the 7-year single-term/Knesset-elected detail alongside
its already-present ceremonial-vs-executive framing.

**Also**: added an `aliases` field to the org schema (JNF/KKL on Jewish National Fund), fixed 5
real person-org gaps found by cross-checking `primary_affiliations` text against `notable_members`
arrays (Weitz→JNF was the one Nick flagged; Ruppin, Ussishkin, Schapira, Shamir were the same
class of gap found by extending the same check dataset-wide), and 2 topic-org gaps (British
Mandate and Balfour Declaration → League of Nations, both already discussed it in their own prose
without the structured link).

36 actors, 24 knesset_members, 42 orgs, 17 laws, 63 topics. Collision check clean throughout, one
wiki publish, one network-prototype publish, one commit.

## Vote-inferred ideology considered and declined; 5 missing party orgs added instead (2026-09-03)

Nick asked whether voting record could be used to assign alignment, using Benny Gantz as the test
case — his own instinct reads Gantz as left-leaning but flagged that instinct might be an
international frame rather than an Israeli one. Real answer: declined the vote-based approach and
explained why, then fixed the actual root cause instead.

**Why not vote-inference**: this dataset's vote ledger is a deliberately narrow, curated subset
(land/settlement bills specifically, per the project's own scope), not a comprehensive roll-call
record. Scoring alignment from it would really measure "voted for settlement expansion," not
general left/right — and would actively mislead on cross-cutting figures exactly like Gantz, who
voted for Ma'ale Adumim sovereignty as a security-establishment centrist for coalition reasons
already flagged elsewhere in this dataset as "complicating any simple coalition/opposition
reading." A single-issue-vote score risks manufacturing a confident-looking wrong answer.

**Root cause found instead**: Gantz, Lapid, Ben-Gvir, Son Har-Melech, and Goldknopf were all
showing as isolated/unaffiliated in the network view not because of a classification bug, but
because their actual parties — National Unity, Blue and White, Yesh Atid, Otzma Yehudit, United
Torah Judaism — were never added as org entries at all. Added all 5, real-researched (founding
dates, platforms, key figures), linked to their MKs via `notable_members`.

**Result validates Nick's own hedge, doesn't contradict it**: run through the existing alignment
classifier (org_type institutional-check, then ideology keywords, then lineage propagation), Gantz
and Lapid land on honest "no data" — Blue and White/National Unity/Yesh Atid are genuinely
centrist with no lineage tie to either the Revisionist-right or Labor-left chains, so the
classifier correctly declines to force them into "left" or "right" rather than picking one.
Ben-Gvir and Son Har-Melech resolve cleanly to "right" via Otzma Yehudit (added "kahanism" /
"ultranationalism" / "far-right" to the right-keyword list, since none of the existing keywords,
all drawn from classical Revisionism, covered a Kahanist party). Goldknopf stays honestly
unaffiliated — United Torah Judaism is genuinely non-Zionist/Haredi, a different axis entirely
from the Revisionist/Labor/Religious-Zionist spectrum this classifier models, not a gap to force
closed.

**Also fixed**: the network prototype crashed on load (`Cannot read properties of undefined
(reading 'push')`) — `buildIndex()` still assumed only 4 node kinds existed after topics were
added as a 5th in the previous round. One-line fix (skip kinds the index has no bucket for).

47 orgs (42→47), 24 knesset_members (5 gained notable_members via reciprocal org links), other
counts unchanged. Collision check clean, wiki + network prototype both republished, one commit.
