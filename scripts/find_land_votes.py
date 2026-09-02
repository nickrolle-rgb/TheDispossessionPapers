#!/usr/bin/env python3
"""
Search the scraped Knesset vote data for land/settlement-relevant bills.

Why this exists instead of a blind SQLite -> knesset_members.json dump: most of the ~2M
scraped vote-result rows have nothing to do with land policy (budget votes, unrelated
legislation, procedural motions). knesset_members.json is a curated, citable file — dumping
everything into it would bury the signal and violate the project's citation discipline (see
SCOPE.md: land_impact fields need a real citation, not an auto-generated guess). This script
is the research tool: it finds CANDIDATE votes by keyword, you (or Claude, reviewing results)
decide which are real land-policy actions worth promoting into the curated JSON with an actual
land_impact description and citation.

Usage:
    python find_land_votes.py                  # run all default keyword groups
    python find_land_votes.py "מקרקעין"          # search one term
    python find_land_votes.py --mk 965          # all land-relevant votes for one person_id
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "knesset_votes.sqlite3"

# Hebrew keyword groups, roughly grouped by theme. Deliberately broad (better to over-match
# and let a human/reviewer discard false positives than to under-match and miss real bills).
KEYWORD_GROUPS = {
    "land / land law": ["אדמות", "אדמת", "קרקע", "מקרקעין"],
    "expropriation": ["הפקעה", "הפקעת"],
    "absentee property": ["נכסי נפקדים", "רכוש נפקדים", "נפקדים"],
    "settlement": ["התנחלות", "התנחלויות", "התיישבות"],
    "planning & building": ["תכנון ובניה", "תכנון ובנייה"],
    "annexation / border": ["סיפוח", "גבול המדינה", "ריבונות"],
    "evacuation / demolition": ["פינוי", "הריסת בתים", "הריסה"],
    "Jewish National Fund / Israel Lands": ["קרן קיימת", "מינהל מקרקעי ישראל", "רשות מקרקעי ישראל"],
}


def search(conn, term):
    q = """
        SELECT v.vote_id, ps.knesset_num, v.vote_date, v.title_he
        FROM votes v
        LEFT JOIN plenum_sessions ps ON v.session_id = ps.session_id
        WHERE v.title_he LIKE ?
        ORDER BY v.vote_date
    """
    return conn.execute(q, (f"%{term}%",)).fetchall()


def vote_breakdown(conn, vote_id):
    q = """
        SELECT r.first_name_he, r.last_name_he, vr.result_label, vr.result_desc_he
        FROM vote_results vr
        JOIN mk_roster r ON vr.mk_id = r.person_id
        WHERE vr.vote_id = ?
    """
    return conn.execute(q, (vote_id,)).fetchall()


def mk_land_votes(conn, person_id):
    all_terms = [t for terms in KEYWORD_GROUPS.values() for t in terms]
    like_clauses = " OR ".join(["v.title_he LIKE ?"] * len(all_terms))
    q = f"""
        SELECT v.vote_id, ps.knesset_num, v.vote_date, v.title_he, vr.result_label
        FROM vote_results vr
        JOIN votes v ON vr.vote_id = v.vote_id
        LEFT JOIN plenum_sessions ps ON v.session_id = ps.session_id
        WHERE vr.mk_id = ? AND ({like_clauses})
        ORDER BY v.vote_date
    """
    return conn.execute(q, [person_id] + [f"%{t}%" for t in all_terms]).fetchall()


def main():
    if not DB_PATH.exists():
        print(f"No database at {DB_PATH} — run knesset_scraper.py first.", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)

    if len(sys.argv) >= 3 and sys.argv[1] == "--mk":
        pid = int(sys.argv[2])
        rows = mk_land_votes(conn, pid)
        print(f"{len(rows)} land-relevant vote(s) for person_id={pid}:")
        for vote_id, kn, date, title, result in rows:
            print(f"  [{date}] KN{kn} vote#{vote_id} -> {result}: {title}")
        return

    if len(sys.argv) >= 2 and not sys.argv[1].startswith("--"):
        terms = [sys.argv[1]]
        groups = {"custom": terms}
    else:
        groups = KEYWORD_GROUPS

    total_unique = set()
    for group_name, terms in groups.items():
        group_hits = []
        for term in terms:
            rows = search(conn, term)
            group_hits.extend(rows)
            total_unique.update(r[0] for r in rows)
        # dedupe within group by vote_id, keep order
        seen = set()
        deduped = []
        for r in group_hits:
            if r[0] not in seen:
                seen.add(r[0])
                deduped.append(r)
        print(f"\n=== {group_name} ({len(deduped)} distinct votes) ===")
        for vote_id, kn, date, title in deduped[:15]:
            kn_str = f"KN{kn}" if kn is not None else "KN?"
            print(f"  [{date}] {kn_str} vote#{vote_id}: {title}")
        if len(deduped) > 15:
            print(f"  ...and {len(deduped) - 15} more")

    print(f"\nTotal distinct candidate votes across all groups: {len(total_unique)}")
    print("(Note: full vote_results pull may still be in progress — this is a snapshot, not final.)")


if __name__ == "__main__":
    main()
