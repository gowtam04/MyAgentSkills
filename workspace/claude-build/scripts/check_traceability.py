#!/usr/bin/env python3
"""Check that every requirement ID the plan cites is proven by at least one test.

Test-writers tag each test with the AC/BR IDs it proves (in the test name or a comment on it).
This script reads the Build Manifest, collects the IDs each phase cites, scans the test files, and
reports cited IDs that no test mentions.

Usage:
  python3 check_traceability.py <plan doc> --root <project root>              # whole build
  python3 check_traceability.py <plan doc> --root <project root> --phase p4a  # one phase's own tests
  ... --extra-tests "tests/integration/**" "tests/e2e/**"                      # also scan these

Rules:
  - every cited AC-… and BR-… must appear in at least one scanned test file;
  - a cited US-… passes if it, or any AC under it, appears;
  - NFR-… IDs are reported but not required.
With --phase, only that phase's `tests` files are scanned (what its reviewer checks). Without it,
all phases' tests plus --extra-tests are scanned (final verification — integration tests count).
Exit code 1 if any required ID is missing. No third-party packages needed.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_manifest import ID_RE, as_list, find_manifest  # noqa: E402


def story_of(ac):
    m = re.match(r"^((?:[A-Z][A-Z0-9]*-)?)AC-(\d+)", ac)
    return f"{m.group(1)}US-{m.group(2)}" if m else None


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
    ap = argparse.ArgumentParser(description="Every cited requirement ID must be proven by a test.")
    ap.add_argument("doc", help="implementation-plan.md or design.md containing the Build Manifest")
    ap.add_argument("--root", default=".", help="project root")
    ap.add_argument("--phase", action="append", help="limit to this phase id (repeatable)")
    ap.add_argument("--extra-tests", nargs="*", default=[], help="extra test globs, e.g. tests/integration/**")
    args = ap.parse_args()
    root = Path(args.root)

    m = find_manifest(Path(args.doc).read_text())
    if m is None:
        sys.exit("ERROR: no Build Manifest found")
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
        found.update(ID_RE.findall(f.read_text(errors="ignore")))

    missing_total = 0
    for p in phases:
        cited = [str(r) for r in as_list(p.get("requirement_refs")) if ID_RE.fullmatch(str(r))]
        if not cited:
            continue
        missing = []
        for rid in cited:
            if rid in found or "-NFR-" in f"-{rid}":
                continue
            if "-US-" in f"-{rid}" and any(story_of(a) == rid for a in found if "-AC-" in f"-{a}"):
                continue
            missing.append(rid)
        status = "ok" if not missing else "MISSING " + ", ".join(missing)
        print(f"{p.get('id'):>8}  {len(cited) - len(missing)}/{len(cited)} cited IDs proven by a test  {status}")
        missing_total += len(missing)

    print(f"\nscanned {len(files)} test files; {len(found)} distinct IDs tagged; {missing_total} cited IDs untested")
    if not files:
        print("WARN  no test files matched — check the `tests` globs and --root")
    sys.exit(1 if missing_total else 0)


if __name__ == "__main__":
    main()
