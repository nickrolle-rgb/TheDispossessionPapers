#!/usr/bin/env python3
"""
Given a vote_id from the completed Knesset scrape, print a structured roll-call breakdown
ready for curation into knesset_members.json.

This is the second half of the research -> promote pipeline find_land_votes.py starts:
    1. find_land_votes.py finds CANDIDATE votes by keyword (720 as of the completed scrape).
    2. A human (or Claude, reviewing) picks a genuinely significant one.
    3. promote_vote.py (this script) pulls that vote's full roll call, with party-at-the-time
       context, so a specific MK's vote can be checked and cited before writing a
       knesset_members.json entry by hand — never auto-generate the entry itself; the
       land_impact description and citation still need a real source and human judgment,
       same discipline as every other file in this project.

Usage:
    python promote_vote.py <vote_id>                    # full roll call, grouped by result
    python promote_vote.py <vote_id> --mk-name "רבין"     # find one MK's vote by Hebrew surname
    python promote_vote.py <vote_id> --against-only       # just the dissenters (often the story)
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "knesset_votes.sqlite3"


def vote_header(conn, vote_id):
    q = """
        SELECT v.vote_id, ps.knesset_num, v.vote_date, v.title_he, v.vote_subject_he,
               v.vote_status_desc_he
        FROM votes v
        LEFT JOIN plenum_sessions ps ON v.session_id = ps.session_id
        WHERE v.vote_id = ?
    """
    return conn.execute(q, (vote_id,)).fetchone()


def roll_call(conn, vote_id, knesset_num, vote_date):
    q = """
        SELECT vr.first_name_he, vr.last_name_he, vr.result_label, mpm.faction_name_he,
               vr.mk_id
        FROM vote_results vr
        LEFT JOIN mk_party_membership mpm
          ON mpm.person_id = vr.mk_id AND mpm.knesset_num = ?
          AND mpm.start_date <= ?
          AND (mpm.finish_date IS NULL OR mpm.finish_date >= ?)
        WHERE vr.vote_id = ?
        ORDER BY vr.result_label, vr.last_name_he
    """
    return conn.execute(q, (knesset_num, vote_date, vote_date, vote_id)).fetchall()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    vote_id = int(sys.argv[1])
    mk_name_filter = None
    against_only = "--against-only" in sys.argv
    if "--mk-name" in sys.argv:
        idx = sys.argv.index("--mk-name")
        mk_name_filter = sys.argv[idx + 1]

    if not DB_PATH.exists():
        print(f"No database at {DB_PATH}", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)

    header = vote_header(conn, vote_id)
    if not header:
        print(f"No vote found with vote_id={vote_id}", file=sys.stderr)
        sys.exit(1)
    vid, kn, date, title, subject, status = header
    print(f"vote_id={vid}  Knesset {kn}  {date}")
    print(f"title:   {title}")
    print(f"subject: {subject}")
    print(f"status:  {status}")
    print()

    rows = roll_call(conn, vote_id, kn, date)
    if mk_name_filter:
        rows = [r for r in rows if mk_name_filter in r[0] or mk_name_filter in r[1]]
    if against_only:
        rows = [r for r in rows if r[2] == "Against"]

    tally = {}
    for r in rows:
        tally[r[2]] = tally.get(r[2], 0) + 1
    print("Tally:", tally)
    print()

    current_result = None
    for first, last, result, faction, mk_id in rows:
        if result != current_result:
            print(f"--- {result} ---")
            current_result = result
        faction_str = faction if faction else "(faction unknown at this date)"
        print(f"  [{mk_id}] {first} {last} — {faction_str}")


if __name__ == "__main__":
    main()
