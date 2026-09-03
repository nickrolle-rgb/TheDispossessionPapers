#!/usr/bin/env python3
"""
Pre-publish integrity check for the Zionism Timeline dataset — mirrors the wiki's own JS
autolink/nameIndex logic in Python so a check can run without a browser. Two things it catches
that a bare `json.load` won't:

1. Name collisions: two different entities (a person, org, law, or topic) that would resolve to
   the same auto-linked name in wiki-prototype.html's prose — the wiki's `nameIndex` can only
   point one name at one entity, so a collision here means one of them will silently mislink
   once the JSON is re-embedded.
2. Dangling references: a `related_actor_ids`/`related_org_ids`/lineage field pointing at an
   entity ID that doesn't exist in any of the six data files — renders as "(not yet profiled)" or
   a broken link instead of failing loudly, so this is the only thing that actually catches it.

Run this — and re-embed via embed_data.py, and eyeball the diff — before every publish. Exits
with status 1 if any collision, dangling reference, or duplicate ID is found (clean run exits 0),
so it's safe to use as a CI gate later if this repo ever gets one.

Usage:
    python scripts/collision_check.py
"""

import json
import collections
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    actors = load("historical_actors.json")
    orgs = load("organizations.json")
    mks = load("knesset_members.json")
    foreign = load("current_foreign_actors.json")
    laws = load("laws.json")
    topics = load("topics.json")

    entities = {}
    for a in actors:
        entities["actor:" + a["actor_id"]] = {"kind": "actor", "data": a, "name": a["full_name"]}
    for o in orgs:
        entities["org:" + o["org_id"]] = {"kind": "org", "data": o, "name": o["name"]}
    for m in mks:
        entities["mk:" + m["mk_id"]] = {"kind": "mk", "data": m, "name": m["full_name"]}
    for f in foreign:
        entities["foreign:" + f["actor_id"]] = {"kind": "foreign", "data": f, "name": f["full_name"]}
    for l in laws:
        entities["law:" + l["law_id"]] = {"kind": "law", "data": l, "name": l["title"]}
    for t in topics:
        entities["topic:" + t["topic_id"]] = {"kind": "topic", "data": t, "name": t["name"]}

    PERSON_KINDS = {"actor", "foreign", "mk"}
    # Same manual aliases the wiki's own JS autolinker carries — keep these two lists in sync by
    # hand; there's no single source of truth for them yet (see SCOPE.md's Open section).
    MANUAL_ALIASES = {
        "IDF": "org:idf",
        "Irgun": "org:irgun",
        "Land Acquisition Law": "law:land-acquisition-law-1953",
    }

    surname_count = collections.Counter()
    for key, e in entities.items():
        if e["kind"] not in PERSON_KINDS:
            continue
        surname = e["name"].split(",")[0].strip().split(" ")[-1]
        if surname and len(surname) > 3:
            surname_count[surname] += 1

    name_index = []  # list of (name, key)
    for key, e in entities.items():
        names = [e["name"]]
        d = e["data"]
        if d.get("birth_name") and d["birth_name"] != e["name"]:
            names.append(d["birth_name"])
        if e["kind"] in PERSON_KINDS:
            surname = e["name"].split(",")[0].strip().split(" ")[-1]
            if surname and len(surname) > 3 and surname_count[surname] == 1:
                names.append(surname)
        if e["kind"] == "org":
            for part in e["name"].split("/"):
                short = part.split("(")[0].strip()
                if short and short != e["name"]:
                    names.append(short)
            for al in d.get("aliases", []):
                names.append(al)
        if e["kind"] == "law":
            short = e["name"].split(",")[0].strip()
            if short and short != e["name"]:
                names.append(short)
        if e["kind"] == "topic" and d.get("aliases"):
            for al in d["aliases"]:
                names.append(al)
        for n in names:
            if n and len(n) > 3:
                name_index.append((n, key))

    for alias, key in MANUAL_ALIASES.items():
        name_index.append((alias, key))

    # Collision check: same name string pointing at more than one distinct key.
    by_name = collections.defaultdict(set)
    for n, key in name_index:
        by_name[n].add(key)
    collisions = {n: sorted(keys) for n, keys in by_name.items() if len(keys) > 1}
    print("Name collisions:", collisions)

    # Dangling related_*/notable_members/lineage references.
    all_actor_mk_ids = {a["actor_id"] for a in actors} | {m["mk_id"] for m in mks}
    all_org_ids = {o["org_id"] for o in orgs}
    dangling = []
    for t in topics:
        for aid in t.get("related_actor_ids", []):
            if aid not in all_actor_mk_ids:
                dangling.append(("topic:" + t["topic_id"], "related_actor_ids", aid))
        for oid in t.get("related_org_ids", []):
            if oid not in all_org_ids:
                dangling.append(("topic:" + t["topic_id"], "related_org_ids", oid))
    for o in orgs:
        for oid in o["lineage"].get("predecessor_orgs", []) + o["lineage"].get("successor_orgs", []):
            # Free-text placeholders like "Gahal (not yet profiled)" are deliberately skipped —
            # only bare IDs that look like they should resolve get flagged.
            if oid not in all_org_ids and "(" not in oid and " " not in oid:
                dangling.append(("org:" + o["org_id"], "lineage", oid))
        mi = o["lineage"].get("merged_into")
        if mi and mi not in all_org_ids:
            dangling.append(("org:" + o["org_id"], "merged_into", mi))
        ck = o["lineage"].get("current_knesset_party_id")
        if ck and ck not in all_org_ids:
            dangling.append(("org:" + o["org_id"], "current_knesset_party_id", ck))
    print("Dangling org/topic references:", dangling)

    # Duplicate topic_ids / org_ids sanity.
    ids = [t["topic_id"] for t in topics]
    dup_ids = [i for i, c in collections.Counter(ids).items() if c > 1]
    print("Duplicate topic_ids:", dup_ids)
    oids = [o["org_id"] for o in orgs]
    dup_oids = [i for i, c in collections.Counter(oids).items() if c > 1]
    print("Duplicate org_ids:", dup_oids)

    if collisions or dangling or dup_ids or dup_oids:
        sys.exit(1)


if __name__ == "__main__":
    main()
