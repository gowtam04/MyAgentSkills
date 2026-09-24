#!/usr/bin/env python3
"""Lint a Game Build Manifest (the ```yaml block with `phases:` in implementation-plan.md or design.md).

Usage:
  python3 check_manifest.py docs/game-architecture/implementation-plan.md [--root .]

Checks (errors fail the run; warnings are printed):
  - phase ids unique; depends_on references exist; no dependency cycles
  - required phase fields: name, depends_on, owns, gdd_refs, kind, test_focus, playtest_focus
  - kind in scaffold|gameplay|content|assets|audio|juice|ui|playtest
  - no path owned by two phases
  - every `shared` path is owned (created) by some phase that the sharing phase depends on,
    directly or transitively, or already exists in the repo
  - gdd_refs files exist (relative to --root)
  - commands run/test/smoke/screenshot are set (TBD allowed only if a scaffold phase exists)
  - assets: unique ids, method in the allowed set, depends_on ids exist, phase exists
  - playtest_checkpoints `after` ids exist
  - warns when a file is `shared` by 3+ phases (a hub file that serializes the build)
Also prints the parallel waves implied by depends_on, the widest wave, and the critical path.
Needs PyYAML (pip install pyyaml). Exit code 1 on errors.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is not installed (pip install pyyaml). Check the manifest by hand against references/ownership-checklist.md.")

KINDS = {"scaffold", "gameplay", "content", "assets", "audio", "juice", "ui", "playtest"}
METHODS = {"code-vector", "code-raster", "procedural", "image-gen", "greybox", "external", "stub"}
REQUIRED = ["name", "depends_on", "owns", "gdd_refs", "kind", "test_focus", "playtest_focus"]


def find_manifest(text):
    for block in re.findall(r"```ya?ml\s*\n(.*?)```", text, re.S):
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as e:
            if "phases:" in block:
                sys.exit(f"ERROR: manifest YAML does not parse: {e}")
            continue
        if isinstance(data, dict) and "phases" in data:
            return data
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--root", default=".", help="project root for resolving gdd_refs and existing files")
    args = ap.parse_args()
    root = Path(args.root)
    m = find_manifest(Path(args.doc).read_text())
    if m is None:
        sys.exit("ERROR: no ```yaml block with a `phases:` key found")

    errors, warnings = [], []
    phases = m.get("phases") or []
    ids = [p.get("id") for p in phases]
    by_id = {p.get("id"): p for p in phases}
    for dup in {i for i in ids if ids.count(i) > 1}:
        errors.append(f"duplicate phase id {dup}")

    for p in phases:
        pid = p.get("id")
        for f in REQUIRED:
            if f not in p:
                errors.append(f"{pid}: missing field `{f}`")
        if p.get("kind") not in KINDS:
            errors.append(f"{pid}: kind `{p.get('kind')}` not in {sorted(KINDS)}")
        for d in p.get("depends_on") or []:
            if d not in by_id:
                errors.append(f"{pid}: depends_on unknown phase `{d}`")
        for r in p.get("gdd_refs") or []:
            if not (root / str(r).split("#")[0]).exists():
                errors.append(f"{pid}: gdd_ref file not found: {r}")
        if not p.get("gdd_refs") and p.get("kind") not in {"scaffold"}:
            warnings.append(f"{pid}: no gdd_refs")

    # cycles + transitive deps
    def ancestors(pid, seen=None, stack=()):
        seen = set() if seen is None else seen
        if pid in stack:
            errors.append(f"dependency cycle through {pid}")
            return seen
        for d in (by_id.get(pid, {}).get("depends_on") or []):
            if d in by_id and d not in seen:
                seen.add(d)
                ancestors(d, seen, stack + (pid,))
        return seen

    owner = {}
    for p in phases:
        for o in p.get("owns") or []:
            if o in owner:
                errors.append(f"`{o}` owned by both {owner[o]} and {p.get('id')}")
            owner[o] = p.get("id")

    for p in phases:
        pid = p.get("id")
        anc = ancestors(pid)
        for s in p.get("shared") or []:
            if s in owner:
                if owner[s] == pid:
                    warnings.append(f"{pid}: `{s}` is both owned and shared by the same phase")
                elif owner[s] not in anc:
                    errors.append(f"{pid}: shares `{s}` but its creator {owner[s]} is not an upstream dependency")
            elif not (root / s).exists():
                errors.append(f"{pid}: shares `{s}` but no phase owns (creates) it and it doesn't exist yet")

    cmds = m.get("commands") or {}
    has_scaffold = any(p.get("kind") == "scaffold" for p in phases)
    for c in ["run", "test", "smoke", "screenshot"]:
        v = str(cmds.get(c, "")).strip()
        if not v or v == "...":
            errors.append(f"commands.{c} is empty")
        elif v.upper().startswith("TBD") and not has_scaffold:
            errors.append(f"commands.{c} is TBD but there is no scaffold phase to set it")

    assets = m.get("assets") or []
    aids = [a.get("id") for a in assets]
    for dup in {i for i in aids if aids.count(i) > 1}:
        errors.append(f"duplicate asset id {dup}")
    for a in assets:
        aid = a.get("id")
        if a.get("method") not in METHODS:
            errors.append(f"asset {aid}: method `{a.get('method')}` not in {sorted(METHODS)}")
        for d in a.get("depends_on") or []:
            if d not in aids:
                errors.append(f"asset {aid}: depends_on unknown asset `{d}`")
        if a.get("phase") not in by_id:
            errors.append(f"asset {aid}: phase `{a.get('phase')}` not found")
        if a.get("method") == "image-gen":
            warnings.append(f"asset {aid}: image-gen — confirm the user has a generation tool, and name a fallback")

    for cp in m.get("playtest_checkpoints") or []:
        for a in cp.get("after") or []:
            if a not in by_id:
                errors.append(f"playtest checkpoint {cp.get('name')}: unknown phase `{a}`")

    # hub files: shared by many phases -> those phases can't overlap
    sharers = {}
    for p in phases:
        for s_ in p.get("shared") or []:
            sharers.setdefault(s_, []).append(p.get("id"))
    for f, ps in sorted(sharers.items()):
        if len(ps) >= 3:
            warnings.append(f"hub file `{f}` is shared by {len(ps)} phases ({', '.join(map(str, ps))}) — "
                            "these phases serialize; consider a single wiring phase + registration points")

    # waves: level = 1 + max(level of deps)
    level = {}
    def lvl(pid, stack=()):
        if pid in level:
            return level[pid]
        if pid in stack:
            return 1
        deps = [d for d in (by_id.get(pid, {}).get("depends_on") or []) if d in by_id]
        level[pid] = 1 + max((lvl(d, stack + (pid,)) for d in deps), default=0)
        return level[pid]
    for pid in by_id:
        lvl(pid)
    if level:
        print("Parallel waves (from depends_on):")
        for w in range(1, max(level.values()) + 1):
            members = [pid for pid in by_id if level[pid] == w]
            print(f"  wave {w}: {', '.join(map(str, members))}")
        widest = max(sum(1 for v in level.values() if v == w) for w in set(level.values()))
        # critical path: follow the deepest dependency back from the deepest phase
        end = max(level, key=level.get)
        path = [end]
        while True:
            deps = [d for d in (by_id[path[-1]].get("depends_on") or []) if d in by_id]
            if not deps:
                break
            path.append(max(deps, key=lambda d: level[d]))
        print(f"  widest wave: {widest} phases; critical path ({len(path)}): {' -> '.join(map(str, reversed(path)))}")
        print("  (phases sharing a file can't truly overlap even within a wave)\n")

    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(phases)} phases, {len(owner)} owned paths, {len(assets)} assets: "
          f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
