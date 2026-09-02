#!/usr/bin/env python3
"""
Re-embed the six curated data/*.json files into wiki-prototype.html as inline JS arrays.

wiki-prototype.html has no build step and no server — it's a single self-contained HTML file
that embeds its own data as `var ACTORS = [...]; var ORGS = [...];` etc., near the top of the
file, and renders everything client-side via hash routing. The JSON files in data/ are the real
source of truth; this script is the only thing that syncs an edit to one of them into the page
that actually gets published. Run it, then scripts/collision_check.py, before every publish —
see SCOPE.md's standing workflow section.

Usage:
    python scripts/embed_data.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_PATH = ROOT / "wiki-prototype.html"

# JS variable name -> source JSON file, in the order they appear in wiki-prototype.html.
FILES = {
    "ACTORS": "data/historical_actors.json",
    "ORGS": "data/organizations.json",
    "MKS": "data/knesset_members.json",
    "FOREIGN": "data/current_foreign_actors.json",
    "LAWS": "data/laws.json",
    "TOPICS": "data/topics.json",
}


def main():
    html = WIKI_PATH.read_text(encoding="utf-8")

    for varname, rel_path in FILES.items():
        data = json.loads((ROOT / rel_path).read_text(encoding="utf-8"))
        js = json.dumps(data, ensure_ascii=False, indent=2)
        pattern = re.compile(r"var " + varname + r" = .*?;\n", re.DOTALL)
        new_block = f"var {varname} = {js};\n"
        html, n = pattern.subn(new_block, html, count=1)
        if n != 1:
            raise SystemExit(
                f"Expected exactly one 'var {varname} = ...;' block in wiki-prototype.html, "
                f"found {n}. Aborting without writing — check the file wasn't restructured."
            )
        print(f"{varname}: replaced ({len(data)} entries)")

    WIKI_PATH.write_text(html, encoding="utf-8")
    print("wiki-prototype.html updated.")


if __name__ == "__main__":
    main()
