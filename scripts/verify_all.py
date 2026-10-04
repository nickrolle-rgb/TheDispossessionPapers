#!/usr/bin/env python
"""Run the project's full pre-publish verification pipeline, in order, and stop on the first failure.

    python scripts/verify_all.py            # run everything
    python scripts/verify_all.py --no-write # skip the two steps that rewrite files (embed + prototype build)

Steps (each mirrors what the manual routine did every round):
  1. data JSON files all parse
  2. scripts/embed_data.py        re-embed the six data files into wiki-prototype.html
  3. scripts/collision_check.py   name collisions / dangling refs / duplicate ids must all be empty
  3b. scripts/check_engagement.py trail steps resolve; every quiz quotation is verbatim in its source entry
  4. syntax check (new Function) of every <script> in wiki-prototype.html
  5. scripts/harness/wiki_harness.js        DOM-stub behaviour checks + dumps the wiki's own graph edges
  6. prototypes/build_network_view.py       rebuild the standalone prototype
  7. syntax check of prototypes/network_view.html
  8. scripts/harness/prototype_harness.js   DOM-stub behaviour checks on the prototype
  9. edge parity: the wiki's edge set (step 5) must be identical to the prototype's GRAPH_DATA edges
 10. banned reader-facing phrasing grep ("already/also in this dataset")
 11. git status of what changed (informational)

The harnesses live in scripts/harness/ on purpose: they were once kept in a session scratchpad and
were lost when it was reset.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NO_WRITE = "--no-write" in sys.argv
failures = []

# Lines the harnesses print as "false" that are known DOM-stub artifacts, not regressions. Verified by running
# the harness against commits from many rounds back: they print false there too.
KNOWN_FALSE = ("intro overlay in body.children",)


def real_false(output):
    return [l for l in output.splitlines()
            if re.search(r":\s*false\s*$", l) and not any(k in l for k in KNOWN_FALSE)]


def run(cmd, env=None, capture=True):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=capture, text=True, encoding="utf-8", errors="replace", env=e)


def step(n, name):
    print(f"\n[{n}] {name}")


def fail(msg):
    failures.append(msg)
    print("   FAIL:", msg)


NODE_SYNTAX = (
    "const fs=require('fs');const h=fs.readFileSync(process.argv[1],'utf8');let bad=0;"
    "[...h.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)].forEach((m,i)=>{try{new Function(m[1])}"
    "catch(e){bad++;console.log('script',i,e.message)}});console.log(bad?'SYNTAX ERRORS':'SYNTAX OK');process.exit(bad?1:0)"
)

# 1 ---------------------------------------------------------------
step(1, "data files parse")
for f in sorted(os.listdir("data")):
    if f.endswith(".json"):
        try:
            json.load(open(os.path.join("data", f), encoding="utf-8"))
        except Exception as ex:
            fail(f"{f}: {ex}")
print("   ok" if not failures else "")

# 2 ---------------------------------------------------------------
if not NO_WRITE:
    step(2, "embed data into wiki-prototype.html")
    r = run([sys.executable, "scripts/embed_data.py"])
    print("   " + r.stdout.strip().replace("\n", "\n   "))
    if r.returncode:
        fail("embed_data.py failed: " + r.stderr[-300:])
else:
    step(2, "embed data (skipped, --no-write)")

# 3 ---------------------------------------------------------------
step(3, "collision / dangling / duplicate check")
r = run([sys.executable, "scripts/collision_check.py"])
print("   " + r.stdout.strip().replace("\n", "\n   "))
clean = ("Name collisions: {}" in r.stdout and "Dangling org/topic references: []" in r.stdout
         and "Duplicate topic_ids: []" in r.stdout and "Duplicate org_ids: []" in r.stdout)
if r.returncode or not clean:
    fail("collision_check not clean")

# 3b --------------------------------------------------------------
step("3b", "engagement data (trails + quiz quotations verbatim)")
r = run([sys.executable, "scripts/check_engagement.py"])
print("   " + (r.stdout + r.stderr).strip().replace(chr(10), chr(10) + "   "))
if r.returncode:
    fail("check_engagement failed")

# 4 ---------------------------------------------------------------
step(4, "wiki-prototype.html script syntax")
r = run(["node", "-e", NODE_SYNTAX, "wiki-prototype.html"])
print("   " + r.stdout.strip())
if r.returncode:
    fail("wiki syntax errors")

# 5 ---------------------------------------------------------------
step(5, "wiki harness (+ edge dump)")
tmp = tempfile.mkdtemp(prefix="dp_verify_")
r = run(["node", "scripts/harness/wiki_harness.js"], env={"SCRATCH_DIR": tmp})
tail = r.stdout.strip().splitlines()
print("   " + "\n   ".join(tail[-3:]))
bad_lines = real_false(r.stdout)
if r.returncode or "ALL HARNESS CHECKS COMPLETED" not in r.stdout:
    fail("wiki harness did not complete: " + (r.stderr or "")[-300:])
if bad_lines:
    fail("wiki harness has false checks: " + "; ".join(bad_lines[:5]))

# 6 ---------------------------------------------------------------
if not NO_WRITE:
    step(6, "rebuild standalone prototype")
    r = run([sys.executable, "prototypes/build_network_view.py"])
    print("   " + "\n   ".join(r.stdout.strip().splitlines()[:5]))
    if r.returncode:
        fail("build_network_view.py failed: " + r.stderr[-300:])
else:
    step(6, "rebuild prototype (skipped, --no-write)")

# 7 ---------------------------------------------------------------
step(7, "prototype script syntax")
r = run(["node", "-e", NODE_SYNTAX, "prototypes/network_view.html"])
print("   " + r.stdout.strip())
if r.returncode:
    fail("prototype syntax errors")

# 8 ---------------------------------------------------------------
step(8, "prototype harness")
r = run(["node", "scripts/harness/prototype_harness.js"])
print("   " + "\n   ".join(r.stdout.strip().splitlines()[-2:]))
bad_lines = real_false(r.stdout)
if r.returncode or "ALL PROTOTYPE HARNESS CHECKS COMPLETED" not in r.stdout:
    fail("prototype harness did not complete: " + (r.stderr or "")[-300:])
if bad_lines:
    fail("prototype harness has false checks: " + "; ".join(bad_lines[:5]))

# 9 ---------------------------------------------------------------
step(9, "edge parity (wiki vs prototype)")
try:
    js = set(open(os.path.join(tmp, "js_edges.txt"), encoding="utf-8").read().split("\n")) - {""}
    html = open("prototypes/network_view.html", encoding="utf-8").read()
    line = next(l for l in html.split("\n") if l.startswith("var GRAPH_DATA = "))
    data = json.loads(re.sub(r";\s*$", "", line[len("var GRAPH_DATA = "):]))
    py = {f"{e['source']}|{e['target']}|{e['kind']}" for e in data["edges"]}
    if js == py:
        print(f"   EDGE PARITY: IDENTICAL ({len(js)} edges)")
    else:
        fail(f"edge parity differs: only-in-wiki={sorted(js - py)[:5]} only-in-prototype={sorted(py - js)[:5]}")
except Exception as ex:
    fail(f"edge parity could not run: {ex}")

# 10 --------------------------------------------------------------
step(10, "banned phrasing")
hits = []
pat = re.compile(r"(already|also) in this dataset", re.I)
for f in ["wiki-prototype.html", "prototypes/network_view.html", "prototypes/network_view_template.html"] + \
         [os.path.join("data", x) for x in os.listdir("data") if x.endswith(".json")]:
    for i, l in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        if pat.search(l):
            hits.append(f"{f}:{i}")
print("   none" if not hits else "   " + ", ".join(hits[:8]))
if hits:
    fail("banned phrasing found")

# 11 --------------------------------------------------------------
step(11, "git status (informational)")
r = run(["git", "status", "--short"])
print("   " + (r.stdout.strip().replace("\n", "\n   ") or "clean"))

print("\n" + ("=" * 60))
if failures:
    print(f"VERIFY FAILED ({len(failures)}):")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("VERIFY OK: every check passed")
