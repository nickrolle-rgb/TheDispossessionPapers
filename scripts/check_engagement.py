#!/usr/bin/env python
"""Integrity check for the reader-engagement data (data/trails.json, data/quiz.json).

These two files power the Trails and "Who said it?" features. They are only trustworthy if every
reference resolves and every quotation really appears in the entry it is credited to, so this runs
as part of scripts/verify_all.py:

  * every trail step points at an entry that exists, and no trail repeats a step
  * every quiz quotation part appears VERBATIM in the text of its source entry
  * the speaker is one of the (four, distinct) choices and every choice is a real actor entry
  * the answer's source entry is a real entry

Exit code 1 on any failure.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIND_FILE = {
    "actor": ("data/historical_actors.json", "actor_id"),
    "org": ("data/organizations.json", "org_id"),
    "mk": ("data/knesset_members.json", "mk_id"),
    "law": ("data/laws.json", "law_id"),
    "topic": ("data/topics.json", "topic_id"),
}


def load(rel):
    return json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


entries = {}
for kind, (rel, idk) in KIND_FILE.items():
    for e in load(rel):
        entries[(kind, e[idk])] = e

problems = []

trails = load("data/trails.json")
seen_trail_ids = set()
for t in trails:
    if t["trail_id"] in seen_trail_ids:
        problems.append(f"duplicate trail id {t['trail_id']}")
    seen_trail_ids.add(t["trail_id"])
    if len(t["steps"]) < 3:
        problems.append(f"trail {t['trail_id']} has fewer than 3 steps")
    seen = set()
    for s in t["steps"]:
        key = (s["kind"], s["id"])
        if key not in entries:
            problems.append(f"trail {t['trail_id']}: step {key} does not exist")
        if key in seen:
            problems.append(f"trail {t['trail_id']}: step {key} repeated")
        seen.add(key)
        if not s.get("teaser"):
            problems.append(f"trail {t['trail_id']}: step {key} has no teaser")

quiz = load("data/quiz.json")
seen_q = set()
for q in quiz:
    qid = q["quiz_id"]
    if qid in seen_q:
        problems.append(f"duplicate quiz id {qid}")
    seen_q.add(qid)
    src = (q["source"]["kind"], q["source"]["id"])
    if src not in entries:
        problems.append(f"quiz {qid}: source {src} does not exist")
    else:
        blob = "\n".join(strings(entries[src]))
        for p in q["parts"]:
            if p not in blob:
                problems.append(f"quiz {qid}: quotation part not found verbatim in {src}: {p[:70]!r}")
    if q["speaker_id"] not in q["choices"]:
        problems.append(f"quiz {qid}: speaker not among choices")
    if len(set(q["choices"])) != 4:
        problems.append(f"quiz {qid}: needs exactly 4 distinct choices")
    for c in q["choices"]:
        if ("actor", c) not in entries:
            problems.append(f"quiz {qid}: choice {c} is not an actor entry")
    if not q.get("context"):
        problems.append(f"quiz {qid}: no context line")

if problems:
    print("ENGAGEMENT DATA PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print(f"engagement data ok: {len(trails)} trails ({sum(len(t['steps']) for t in trails)} steps), {len(quiz)} quiz questions")
