#!/usr/bin/env python3
"""Check that every GDD section a tested phase cites is proven by at least one test.

Test-writers tag each test with a `gdd:` tag for each gdd_ref it proves (in the test name or a
comment on it). A ref normalizes to `gdd:<file stem>#<anchor>`:
  docs/gdd/03-systems.md#combat  ->  gdd:03-systems#combat
  docs/gdd/02-core-loop.md       ->  gdd:02-core-loop
This script reads the Game Build Manifest, collects the refs each phase with `tests` cites, scans
the test files, and reports cited refs that no test is tagged with.

Usage:
  python3 check_traceability.py <plan doc> --root <project root>              # whole build
  python3 check_traceability.py <plan doc> --root <project root> --phase p3a  # one phase's own tests
  ... --extra-tests "tests/integration/**"                                     # also scan these

Rules:
  - only phases that own `tests` are checked; assets, juice, audio and other phases verified by
    playtest or review aren't;
  - a cited file-level ref (no #anchor) passes if any tag on that file appears.
With --phase, only that phase's `tests` files are scanned (what its reviewer checks). Without it,
all phases' tests plus --extra-tests are scanned (final verification — integration tests count).
Exit code 1 if any cited ref is missing. No third-party packages needed.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_manifest import as_list, find_manifest, gdd_tag  # noqa: E402

TAG_RE = re.compile(r"gdd:[A-Za-z0-9_.\-]+(?:#[A-Za-z0-9_\-]+)?")


def expand(root, patterns):
    files = set()
    for pat in patterns:
        pat = str(pat)
        hits = [root / pat] if not any(c in pat for c in "*?[") else list(root.glob(pat))
        for h in hits:
            if h.is_file():
                files.add(h)
            elif h.is_dir():
                files.update(p for p in h.rglob("*") if p.is_file())
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description="Every cited GDD ref of a tested phase must be proven by a test.")
    ap.add_argument("doc", help="implementation-plan.md or design.md containing the Game Build Manifest")
    ap.add_argument("--root", default=".", help="project root")
    ap.add_argument("--phase", action="append", help="limit to this phase id (repeatable)")
    ap.add_argument("--extra-tests", nargs="*", default=[], help="extra test globs, e.g. tests/integration/**")
    args = ap.parse_args()
    root = Path(args.root)

    m = find_manifest(Path(args.doc).read_text())
    if m is None:
        sys.exit("ERROR: no Game Build Manifest found")
    phases = [p for p in as_list(m.get("phases")) if isinstance(p, dict)]
    if args.phase:
        unknown = set(args.phase) - {p.get("id") for p in phases}
        if unknown:
            sys.exit(f"ERROR: unknown phase id(s): {', '.join(sorted(unknown))}")
        phases = [p for p in phases if p.get("id") in args.phase]

    patterns = [t for p in phases for t in as_list(p.get("tests"))]
    if not args.phase:
        patterns += args.extra_tests
    files = expand(root, patterns)
    found = set()
    for f in files:
        found.update(TAG_RE.findall(f.read_text(errors="ignore")))

    missing_total = 0
    for p in phases:
        if not as_list(p.get("tests")):
            continue
        cited = [gdd_tag(r) for r in as_list(p.get("gdd_refs"))]
        if not cited:
            continue
        missing = []
        for tag in cited:
            if tag in found:
                continue
            if "#" not in tag and any(t.startswith(tag + "#") for t in found):
                continue
            missing.append(tag)
        status = "ok" if not missing else "MISSING " + ", ".join(missing)
        print(f"{p.get('id'):>8}  {len(cited) - len(missing)}/{len(cited)} cited refs proven by a test  {status}")
        missing_total += len(missing)

    print(f"\nscanned {len(files)} test files; {len(found)} distinct gdd tags; {missing_total} cited refs untested")
    if not files:
        print("WARN  no test files matched — check the `tests` globs and --root")
    sys.exit(1 if missing_total else 0)


if __name__ == "__main__":
    main()
