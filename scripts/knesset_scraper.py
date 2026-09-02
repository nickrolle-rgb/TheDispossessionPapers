#!/usr/bin/env python3
"""
Knesset OData scraper — Zionism Timeline project.

Pulls Knesset Member roster, faction history, and roll-call vote data directly from the
Knesset's own official OData services (not scraped HTML, not a third party).

ROSTER/FACTIONS — legacy v3 service, still fine for this (small, static-ish data):
  ParliamentInfo.svc  https://knesset.gov.il/Odata/ParliamentInfo.svc/
    - KNS_Person            all persons (1,188 rows as of 2026-08-31, includes non-MK officials)
    - KNS_PersonToPosition  person <-> position history, incl. "Member of Knesset" (PositionID=43)
    - KNS_Faction           faction id -> name, per Knesset term

VOTES — v4 service. CONFIRMED LIVE 2026-08-31: the legacy v3 Votes.svc
(vote_rslts_kmmbr_shadow / View_vote_rslts_hdr_Approved — "shadow" was the tell) stopped
updating at Knesset 24, mid-2021, and was DROPPED in favor of v4 below. Found via web search
after noticing the v3 data looked stale; verified live before switching.
  OdataV4/ParliamentInfo  https://knesset.gov.il/OdataV4/ParliamentInfo/
    - KNS_PlenumVote        one row per vote (36,183 rows, current through 2026-07-28 as of
                             this writing — genuinely near-live, not a stale snapshot)
    - KNS_PlenumVoteResult  one row per MK per vote (1,953,709 rows as of 2026-08-31).
                             MkId here is THE SAME ID SPACE as KNS_Person.Id (confirmed live:
                             MkId 466 <-> KNS_Person Id 466, same name both sides) — v3's
                             person<->voter ID mismatch problem does not exist in v4.
    - KNS_PlenumSession      SessionID -> KnessetNum lookup (KNS_PlenumVote itself has no
                             KnessetNum field; join via SessionID to get it)

CONFIRMED LIVE 2026-08-31: individual (roll-call) vote records only exist from Knesset 16
(2003) onward regardless of v3/v4 — filtering pre-Knesset-16 in either service returns
nothing. Knessets 1-15 (1949-2003) have no per-MK vote data in either API; that period stays
manual/narrative, same as the Kaplan/Eshkol calibration entries already in knesset_members.json.

STORAGE: the vote_results table is ~2M rows — far too large for a single pretty-printed JSON
array (would be a ~250-300MB unopenable file). Output goes to SQLite
(data/knesset_votes.sqlite3). The small roster/faction tables also get a JSON export for
convenience, since those are a few thousand rows total.

Usage:
    python knesset_scraper.py roster        # ~1,188 rows, fast, writes JSON + sqlite
    python knesset_scraper.py factions      # small, fast, writes JSON + sqlite
    python knesset_scraper.py sessions      # ~few thousand rows, fast — SessionID->KnessetNum
    python knesset_scraper.py vote_headers  # 36,183 rows, several minutes
    python knesset_scraper.py vote_results  # ~1.95M rows, SLOW (expect 3+ hours at the 100-row
                                             # server-side page cap), resumable — safe to
                                             # interrupt and rerun, picks up from checkpoint
    python knesset_scraper.py all           # runs all of the above in order
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

import requests

PARLIAMENT_BASE = "https://knesset.gov.il/Odata/ParliamentInfo.svc"       # v3 — roster/factions only
VOTES_BASE_V4 = "https://knesset.gov.il/OdataV4/ParliamentInfo"           # v4 — all vote data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "knesset_votes.sqlite3"

PAGE_SIZE = 100  # CONFIRMED LIVE 2026-08-31: server hard-caps every response at 100 rows
                 # regardless of what $top requests — full vote_results pull (1.27M rows) is
                 # therefore ~12,758 requests. At REQUEST_DELAY_SEC below, expect 2+ hours.
REQUEST_DELAY_SEC = 0.25  # polite rate limit — this is a public government server, not ours
MAX_RETRIES = 4

MK_POSITION_ID = 43     # confirmed live 2026-08-31: KNS_Position 43 = "חבר הכנסת" (Member of Knesset)
PARTY_POSITION_ID = 54  # confirmed live 2026-08-31: KNS_Position 54 = "חבר/ת סיעה" (Faction Member) —
                         # THIS is where FactionID/FactionName actually live, not on PositionID 43 records

VOTE_RESULT_LABELS = {
    # confirmed live 2026-08-31 by sampling KNS_PlenumVoteResult.ResultCode/ResultDesc directly
    # (v4 has no separate lookup entity found for this — sampled from data instead). Codes seen
    # so far: 6-9. No "Absent" code observed — v4's table may simply omit MKs who weren't
    # present, unlike v3's explicit Absent code. Treat any other code as genuinely unmapped,
    # not a bug — the raw Hebrew ResultDesc is always stored alongside this label regardless.
    6: "Present (no vote recorded)",  # נוכח
    7: "For",                         # בעד
    8: "Against",                     # נגד
    9: "Abstain",                     # נמנע
}


def _get(url: str, params: dict) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=45, headers={"Accept": "application/json"})
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt == MAX_RETRIES:
                raise
            wait = 2 ** attempt
            print(f"  [retry {attempt}/{MAX_RETRIES}] {exc} — waiting {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def fetch_all(base: str, entity: str, filter_: str | None = None, select: str | None = None,
              page_size: int = PAGE_SIZE, progress_every: int = 20):
    """Generator yielding every row of an OData entity, paginating with $skip/$top."""
    skip = 0
    page_num = 0
    while True:
        params = {"$format": "json", "$top": page_size, "$skip": skip}
        if filter_:
            params["$filter"] = filter_
        if select:
            params["$select"] = select
        data = _get(f"{base}/{entity}", params)
        rows = data.get("value", [])
        if not rows:
            break
        for row in rows:
            yield row
        page_num += 1
        if page_num % progress_every == 0:
            print(f"  ...{entity}: {skip + len(rows)} rows fetched so far")
        skip += len(rows)
        # NOTE: the Knesset OData server silently caps actual page size (observed: 100) below
        # whatever $top requests — do NOT use "len(rows) < page_size" as the stop condition,
        # it fires after page 1 and truncates the pull. Only an empty page means "done".
        time.sleep(REQUEST_DELAY_SEC)


def get_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS mk_roster (
            person_id INTEGER PRIMARY KEY,
            last_name_he TEXT,
            first_name_he TEXT,
            gender_desc_he TEXT,
            is_current INTEGER,
            last_updated TEXT
        );
        CREATE TABLE IF NOT EXISTS mk_terms (
            person_to_position_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            knesset_num INTEGER,
            start_date TEXT,
            finish_date TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_mk_terms_person ON mk_terms(person_id);
        CREATE TABLE IF NOT EXISTS mk_party_membership (
            person_to_position_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            knesset_num INTEGER,
            faction_id INTEGER,
            faction_name_he TEXT,
            start_date TEXT,
            finish_date TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_party_person ON mk_party_membership(person_id);
        CREATE TABLE IF NOT EXISTS factions (
            faction_id INTEGER,
            knesset_num INTEGER,
            name_he TEXT,
            start_date TEXT,
            finish_date TEXT,
            is_current INTEGER,
            PRIMARY KEY (faction_id, knesset_num)
        );
        CREATE TABLE IF NOT EXISTS plenum_sessions (
            session_id INTEGER PRIMARY KEY,
            knesset_num INTEGER,
            session_number INTEGER,
            start_date TEXT,
            finish_date TEXT
        );
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER PRIMARY KEY,
            session_id INTEGER,     -- join to plenum_sessions for knesset_num
            vote_date TEXT,
            title_he TEXT,          -- VoteTitle
            vote_subject_he TEXT,   -- VoteSubject (e.g. which reading/clauses)
            vote_status_code INTEGER,
            vote_status_desc_he TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_votes_session ON votes(session_id);
        CREATE TABLE IF NOT EXISTS vote_results (
            vote_id INTEGER,
            mk_id INTEGER,         -- SAME id space as mk_roster.person_id (KNS_Person.Id) — v4 fixed the v3 mismatch
            vote_date TEXT,
            result_code INTEGER,
            result_label TEXT,     -- best-effort English (see VOTE_RESULT_LABELS); raw Hebrew always kept alongside
            result_desc_he TEXT,
            last_name_he TEXT,
            first_name_he TEXT,
            PRIMARY KEY (vote_id, mk_id)
        );
        CREATE INDEX IF NOT EXISTS idx_vote_results_mk ON vote_results(mk_id);
        CREATE INDEX IF NOT EXISTS idx_vote_results_vote ON vote_results(vote_id);
        CREATE TABLE IF NOT EXISTS _scrape_progress (
            table_name TEXT PRIMARY KEY,
            last_skip INTEGER,
            updated_at TEXT
        );
        """
    )
    conn.commit()
    return conn


def scrape_roster():
    print("Fetching KNS_Person (all persons, incl. non-MK officials)...")
    conn = get_db()
    persons = list(fetch_all(PARLIAMENT_BASE, "KNS_Person"))
    conn.executemany(
        "INSERT OR REPLACE INTO mk_roster VALUES (?,?,?,?,?,?)",
        [
            (p["PersonID"], p.get("LastName"), p.get("FirstName"), p.get("GenderDesc"),
             1 if p.get("IsCurrent") else 0, p.get("LastUpdatedDate"))
            for p in persons
        ],
    )
    conn.commit()
    print(f"  {len(persons)} persons written to mk_roster.")

    print(f"Fetching KNS_PersonToPosition filtered to PositionID={MK_POSITION_ID} (Member of Knesset)...")
    terms = list(fetch_all(PARLIAMENT_BASE, "KNS_PersonToPosition", filter_=f"PositionID eq {MK_POSITION_ID}"))
    conn.executemany(
        "INSERT OR REPLACE INTO mk_terms VALUES (?,?,?,?,?)",
        [
            (t["PersonToPositionID"], t["PersonID"], t.get("KnessetNum"), t.get("StartDate"), t.get("FinishDate"))
            for t in terms
        ],
    )
    conn.commit()
    print(f"  {len(terms)} MK term records written to mk_terms.")
    conn.close()

    # Small enough for a JSON export too, for readability / consistency with the other data files
    mk_ids_with_terms = {t["PersonID"] for t in terms}
    roster_export = [
        {
            "person_id": p["PersonID"],
            "last_name_he": p.get("LastName"),
            "first_name_he": p.get("FirstName"),
            "is_current": bool(p.get("IsCurrent")),
        }
        for p in persons
        if p["PersonID"] in mk_ids_with_terms
    ]
    out_path = DATA_DIR / "knesset_roster_raw.json"
    out_path.write_text(json.dumps(roster_export, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote {len(roster_export)} confirmed MKs to {out_path.name} "
          f"(raw scrape output — NOT the locked knesset_members.json schema; see transform step)")


def scrape_party_membership():
    print(f"Fetching KNS_PersonToPosition filtered to PositionID={PARTY_POSITION_ID} "
          f"(Faction Member — this is where real party affiliation per term lives)...")
    conn = get_db()
    rows = list(fetch_all(PARLIAMENT_BASE, "KNS_PersonToPosition", filter_=f"PositionID eq {PARTY_POSITION_ID}"))
    conn.executemany(
        "INSERT OR REPLACE INTO mk_party_membership VALUES (?,?,?,?,?,?,?)",
        [
            (r["PersonToPositionID"], r["PersonID"], r.get("KnessetNum"), r.get("FactionID"),
             r.get("FactionName"), r.get("StartDate"), r.get("FinishDate"))
            for r in rows
        ],
    )
    conn.commit()
    conn.close()
    print(f"  {len(rows)} party-membership records written to mk_party_membership.")


def scrape_factions():
    print("Fetching KNS_Faction...")
    conn = get_db()
    factions = list(fetch_all(PARLIAMENT_BASE, "KNS_Faction"))
    conn.executemany(
        "INSERT OR REPLACE INTO factions VALUES (?,?,?,?,?,?)",
        [
            (f["FactionID"], f.get("KnessetNum"), f.get("Name"), f.get("StartDate"),
             f.get("FinishDate"), 1 if f.get("IsCurrent") else 0)
            for f in factions
        ],
    )
    conn.commit()
    conn.close()
    print(f"  {len(factions)} faction records written to factions.")


def scrape_sessions():
    print("Fetching KNS_PlenumSession (SessionID -> KnessetNum lookup)...")
    conn = get_db()
    rows = list(fetch_all(VOTES_BASE_V4, "KNS_PlenumSession"))
    conn.executemany(
        "INSERT OR REPLACE INTO plenum_sessions VALUES (?,?,?,?,?)",
        [
            (s["Id"], s.get("KnessetNum"), s.get("Number"), s.get("StartDate"), s.get("FinishDate"))
            for s in rows
        ],
    )
    conn.commit()
    conn.close()
    print(f"  {len(rows)} plenum sessions written to plenum_sessions.")


def scrape_vote_headers():
    print("Fetching KNS_PlenumVote (vote headers, v4 — 36,183 rows as of 2026-08-31, "
          "current through 2026-07-28)...")
    conn = get_db()
    count = 0
    batch = []
    for row in fetch_all(VOTES_BASE_V4, "KNS_PlenumVote"):
        batch.append((
            row["Id"], row.get("SessionID"), row.get("VoteDateTime"), row.get("VoteTitle"),
            row.get("VoteSubject"), row.get("VoteStatusCode"), row.get("VoteStatusDesc"),
        ))
        count += 1
        if len(batch) >= 2000:
            conn.executemany("INSERT OR REPLACE INTO votes VALUES (?,?,?,?,?,?,?)", batch)
            conn.commit()
            batch = []
    if batch:
        conn.executemany("INSERT OR REPLACE INTO votes VALUES (?,?,?,?,?,?,?)", batch)
        conn.commit()
    conn.close()
    print(f"  {count} vote headers written to votes.")


def scrape_vote_results(resume: bool = True):
    """The big one — ~1.95M rows (v4). Resumable: checkpoints $skip into _scrape_progress."""
    conn = get_db()
    skip = 0
    if resume:
        row = conn.execute(
            "SELECT last_skip FROM _scrape_progress WHERE table_name = 'vote_results_v4'"
        ).fetchone()
        if row:
            skip = row[0]
            print(f"Resuming vote_results scrape from skip={skip}")

    print("Fetching KNS_PlenumVoteResult (per-MK vote results, v4 — ~1.95M rows, this will "
          "take hours at the 100-row server page cap; safe to interrupt and rerun, it resumes "
          "from the last checkpoint)...")
    total = 0
    batch = []
    page_num = 0
    current_skip = skip
    consecutive_page_failures = 0
    while True:
        params = {"$top": PAGE_SIZE, "$skip": current_skip}
        try:
            data = _get(f"{VOTES_BASE_V4}/KNS_PlenumVoteResult", params)
        except (requests.RequestException, ValueError) as exc:
            # _get() already retried MAX_RETRIES times internally and still failed — this means
            # sustained server-side slowness/throttling, not a one-off blip. Flush what we have,
            # checkpoint, back off longer, and keep going rather than crashing the whole job —
            # a multi-hour scrape dying on one bad patch and needing a manual restart is worse
            # than just waiting it out.
            consecutive_page_failures += 1
            if batch:
                conn.executemany("INSERT OR REPLACE INTO vote_results VALUES (?,?,?,?,?,?,?,?)", batch)
                conn.execute(
                    "INSERT OR REPLACE INTO _scrape_progress VALUES ('vote_results_v4', ?, datetime('now'))",
                    (current_skip,),
                )
                conn.commit()
                batch = []
            cooldown = min(300, 30 * consecutive_page_failures)  # cap at 5 min
            print(f"  [page failure {consecutive_page_failures}] {exc} — checkpointed at "
                  f"skip={current_skip}, cooling down {cooldown}s before retrying", file=sys.stderr)
            time.sleep(cooldown)
            continue  # retry the SAME current_skip, don't advance
        consecutive_page_failures = 0
        rows = data.get("value", [])
        if not rows:
            break
        for r in rows:
            code = r.get("ResultCode")
            batch.append((
                r.get("VoteID"), r.get("MkId"), r.get("VoteDate"), code,
                VOTE_RESULT_LABELS.get(code, f"Unknown (code {code})"), r.get("ResultDesc"),
                r.get("LastName"), r.get("FirstName"),
            ))
        total += len(rows)
        current_skip += len(rows)
        page_num += 1

        if len(batch) >= 5000:
            conn.executemany(
                "INSERT OR REPLACE INTO vote_results VALUES (?,?,?,?,?,?,?,?)", batch
            )
            conn.execute(
                "INSERT OR REPLACE INTO _scrape_progress VALUES ('vote_results_v4', ?, datetime('now'))",
                (current_skip,),
            )
            conn.commit()
            batch = []

        if page_num % 20 == 0:
            print(f"  ...vote_results: {current_skip} rows fetched so far")

        # see fetch_all() note: server caps real page size below PAGE_SIZE, so only stop on empty
        time.sleep(REQUEST_DELAY_SEC)

    if batch:
        conn.executemany("INSERT OR REPLACE INTO vote_results VALUES (?,?,?,?,?,?,?,?)", batch)
        conn.execute(
            "INSERT OR REPLACE INTO _scrape_progress VALUES ('vote_results_v4', ?, datetime('now'))",
            (current_skip,),
        )
        conn.commit()

    conn.close()
    print(f"  Done. {total} new/updated vote_results rows fetched this run (final skip={current_skip}).")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {
        "roster", "party_membership", "factions", "sessions", "vote_headers", "vote_results", "all"
    }:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd in ("roster", "all"):
        scrape_roster()
    if cmd in ("party_membership", "all"):
        scrape_party_membership()
    if cmd in ("factions", "all"):
        scrape_factions()
    if cmd in ("sessions", "all"):
        scrape_sessions()
    if cmd in ("vote_headers", "all"):
        scrape_vote_headers()
    if cmd in ("vote_results", "all"):
        scrape_vote_results()


if __name__ == "__main__":
    main()
