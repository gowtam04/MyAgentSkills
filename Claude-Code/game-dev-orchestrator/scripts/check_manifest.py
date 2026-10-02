#!/usr/bin/env python3
"""Validate a Game Build Manifest — the ```yaml block with a `phases:` key in implementation-plan.md
or design.md (schema: references/pipeline-contract.md).

Usage:
  python3 check_manifest.py docs/game-architecture/implementation-plan.md [--root .]

Errors (exit code 1):
  - missing/duplicate phase ids, unknown depends_on, dependency cycles
  - missing required fields; unknown `kind` or `risk`; gameplay phases without `tests`
  - a path owned by two phases, a path in both `owns` and `tests`, a concrete path inside another
    phase's glob
  - a `shared` path whose creator isn't an upstream dependency, or that nobody creates and doesn't
    exist yet
  - gdd_refs whose file doesn't exist (relative to --root)
  - commands.run / test / smoke / screenshot empty, or TBD without a scaffold phase
  - assets: duplicate ids, unknown `method`, unknown asset depends_on, unknown owning phase
  - playtest checkpoints pointing at unknown phases
Warnings: overlapping globs, hub files shared by 3+ phases, phases without gdd_refs, asset paths
outside their phase's `owns`, image-gen assets, test_one without {files}, missing typecheck.
Also prints the parallel waves implied by depends_on, the widest wave, and the critical path.

Needs no third-party packages: uses PyYAML when installed, otherwise a built-in parser for the
YAML subset the contract allows (block mappings/lists, [a, b] and {k: v} flow collections, plain
or quoted scalars, # comments).
"""
import argparse
import fnmatch
import re
import sys
from pathlib import Path

KINDS = {"scaffold", "contracts", "gameplay", "content", "assets", "audio", "juice", "ui", "wiring",
         "playtest", "docs"}
TEST_FIRST_KINDS = {"gameplay"}
NO_REFS_OK_KINDS = {"scaffold", "contracts", "wiring", "docs"}
RISKS = {"normal", "high"}
METHODS = {"code-vector", "code-raster", "procedural", "image-gen", "greybox", "external", "stub"}
REQUIRED = ["name", "kind", "depends_on", "owns", "gdd_refs", "test_focus", "playtest_focus"]
WILDCARDS = set("*?[")


# ---------------------------------------------------------------- minimal YAML subset parser
class ManifestError(Exception):
    pass


def _strip_comment(line):
    out, quote = [], None
    for i, ch in enumerate(line):
        prev = line[i - 1] if i else " "
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'" and prev in " \t[{,:":
            quote = ch
            out.append(ch)
        elif ch == "#" and prev in " \t":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _find_colon(text):
    """Index of the mapping colon (':' followed by space/end) outside quotes and brackets, or -1."""
    quote, depth = None, 0
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else " "
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'" and prev in " \t[{,:":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == ":" and depth == 0 and (i + 1 == len(text) or text[i + 1] in " \t"):
            return i
    return -1


def _scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        inner = s[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\") if s[0] == '"' else inner.replace("''", "'")
    low = s.lower()
    if low in ("", "null", "~"):
        return None
    if low in ("true", "false"):
        return low == "true"
    for cast in (int, float):
        try:
            return cast(s)
        except ValueError:
            pass
    return s


def _flow(s, i):
    """Parse a [..] or {..} flow collection starting at s[i]; return (value, next_index)."""
    close = "]" if s[i] == "[" else "}"
    is_map = s[i] == "{"
    i += 1
    items, mapping = [], {}
    while True:
        while i < len(s) and s[i] in " \t,":
            i += 1
        if i >= len(s):
            raise ManifestError(f"unterminated flow collection: {s}")
        if s[i] == close:
            return (mapping if is_map else items), i + 1
        key = None
        if is_map:
            j = i
            if s[j] in "\"'":
                end = s.index(s[j], j + 1)
                key, j = _scalar(s[j:end + 1]), end + 1
            else:
                while j < len(s) and s[j] not in ":,}":
                    j += 1
                key = _scalar(s[i:j])
            if j >= len(s) or s[j] != ":":
                raise ManifestError(f"expected ':' in flow mapping: {s}")
            i = j + 1
            while i < len(s) and s[i] in " \t":
                i += 1
        if i < len(s) and s[i] in "[{":
            val, i = _flow(s, i)
        elif i < len(s) and s[i] in "\"'":
            end = s.index(s[i], i + 1)
            val, i = _scalar(s[i:end + 1]), end + 1
        else:
            j = i
            while j < len(s) and s[j] not in "," + close:
                j += 1
            val, i = _scalar(s[i:j]), j
        if is_map:
            mapping[key] = val
        else:
            items.append(val)


def _value(s):
    s = s.strip()
    if s[:1] in ("[", "{"):
        val, end = _flow(s, 0)
        if s[end:].strip():
            raise ManifestError(f"unexpected text after flow collection: {s}")
        return val
    return _scalar(s)


def _block(lines, i, indent):
    if lines[i][1].startswith("- ") or lines[i][1] == "-":
        return _block_list(lines, i, indent)
    return _block_map(lines, i, indent)


def _block_list(lines, i, indent):
    out = []
    while i < len(lines) and lines[i][0] == indent and (lines[i][1].startswith("- ") or lines[i][1] == "-"):
        text = lines[i][1]
        rest = text[1:].lstrip()
        if not rest:
            if i + 1 < len(lines) and lines[i + 1][0] > indent:
                val, i = _block(lines, i + 1, lines[i + 1][0])
            else:
                val, i = None, i + 1
            out.append(val)
            continue
        if rest[0] not in "[{\"'" and _find_colon(rest) >= 0:
            lines[i] = (indent + len(text) - len(rest), rest, lines[i][2])
            val, i = _block_map(lines, i, lines[i][0])
        else:
            val, i = _value(rest), i + 1
        out.append(val)
    return out, i


def _block_map(lines, i, indent):
    out = {}
    while i < len(lines) and lines[i][0] == indent and not lines[i][1].startswith("- "):
        text, lineno = lines[i][1], lines[i][2]
        c = _find_colon(text)
        if c < 0:
            raise ManifestError(f"manifest line {lineno}: expected 'key: value', got: {text}")
        key, rest = _scalar(text[:c]), text[c + 1:].strip()
        i += 1
        if rest:
            out[key] = _value(rest)
        elif i < len(lines) and (lines[i][0] > indent or (lines[i][0] == indent and lines[i][1].startswith("- "))):
            out[key], i = _block(lines, i, lines[i][0])
        else:
            out[key] = None
    return out, i


def parse_yaml_subset(block):
    lines = []
    for n, raw in enumerate(block.splitlines(), 1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise ManifestError(f"manifest line {n}: tabs are not allowed for indentation")
        text = _strip_comment(raw)
        if text.strip():
            lines.append((len(text) - len(text.lstrip()), text.strip(), n))
    if not lines:
        return None
    val, i = _block(lines, 0, lines[0][0])
    if i < len(lines):
        raise ManifestError(f"manifest line {lines[i][2]}: unexpected indentation: {lines[i][1]}")
    return val


def load_block(block):
    try:
        import yaml  # noqa: WPS433
        return yaml.safe_load(block)
    except ImportError:
        return parse_yaml_subset(block)


def find_manifest(text):
    for block in re.findall(r"^[ \t]*```ya?ml[^\n]*\n(.*?)^[ \t]*```", text, re.S | re.M):
        if not re.search(r"^\s*phases\s*:", block, re.M):
            continue
        try:
            data = load_block(block)
        except Exception as e:  # yaml.YAMLError or ManifestError
            sys.exit(f"ERROR: manifest does not parse: {e}")
        if isinstance(data, dict) and "phases" in data:
            return data
    return None


# ---------------------------------------------------------------- checks
def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def is_glob(p):
    return any(ch in WILDCARDS for ch in p)


def static_prefix(p):
    out = []
    for part in p.split("/"):
        if is_glob(part):
            break
        out.append(part)
    return "/".join(out)


def matches(path, pattern):
    return fnmatch.fnmatchcase(path, pattern) or fnmatch.fnmatchcase(path, pattern.replace("/**/", "/"))


def gdd_tag(ref):
    """docs/gdd/03-systems.md#combat -> gdd:03-systems#combat ; docs/gdd/02-loop.md -> gdd:02-loop"""
    ref = str(ref).strip()
    path, _, anchor = ref.partition("#")
    stem = Path(path).stem if path else ""
    return f"gdd:{stem}#{anchor}" if anchor else f"gdd:{stem}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("doc", help="implementation-plan.md or design.md containing the manifest")
    ap.add_argument("--root", default=".", help="project root, for gdd_refs and files that already exist")
    args = ap.parse_args()
    root = Path(args.root)

    m = find_manifest(Path(args.doc).read_text())
    if m is None:
        sys.exit("ERROR: no ```yaml block with a `phases:` key found")

    errors, warnings = [], []
    phases = [p for p in as_list(m.get("phases")) if isinstance(p, dict)]
    if not phases:
        sys.exit("ERROR: `phases` is empty")
    ids = [p.get("id") for p in phases]
    by_id = {p.get("id"): p for p in phases if p.get("id") is not None}
    if None in ids:
        errors.append("a phase has no `id`")
    for dup in sorted({str(i) for i in ids if ids.count(i) > 1}):
        errors.append(f"duplicate phase id `{dup}`")

    # -- per-phase fields
    for p in phases:
        pid = p.get("id")
        for f in REQUIRED:
            if f not in p:
                errors.append(f"{pid}: missing field `{f}`")
        kind = p.get("kind")
        if kind not in KINDS:
            errors.append(f"{pid}: kind `{kind}` not in {sorted(KINDS)}")
        if p.get("risk", "normal") not in RISKS:
            errors.append(f"{pid}: risk `{p.get('risk')}` must be normal or high")
        if kind in TEST_FIRST_KINDS and not as_list(p.get("tests")):
            errors.append(f"{pid}: `{kind}` phase has no `tests` — spec-first verification needs owned test files")
        for d in as_list(p.get("depends_on")):
            if d not in by_id:
                errors.append(f"{pid}: depends_on unknown phase `{d}`")

    # -- cycles and ancestors
    ancestors_cache = {}

    def ancestors(pid, stack=()):
        if pid in ancestors_cache:
            return ancestors_cache[pid]
        if pid in stack:
            errors.append(f"dependency cycle: {' -> '.join(map(str, stack + (pid,)))}")
            return set()
        out = set()
        for d in as_list(by_id.get(pid, {}).get("depends_on")):
            if d in by_id:
                out.add(d)
                out |= ancestors(d, stack + (pid,))
        ancestors_cache[pid] = out
        return out

    for pid in by_id:
        ancestors(pid)

    # -- ownership
    entries = []  # (pattern, phase, field)
    for p in phases:
        for field in ("owns", "tests"):
            for o in as_list(p.get(field)):
                entries.append((str(o), p.get("id"), field))
    seen = {}
    for pat, pid, field in entries:
        if pat in seen:
            other_pid, other_field = seen[pat]
            if other_pid == pid:
                errors.append(f"{pid}: `{pat}` is in both `{other_field}` and `{field}`")
            else:
                errors.append(f"`{pat}` owned by both {other_pid} ({other_field}) and {pid} ({field})")
        else:
            seen[pat] = (pid, field)
    for a in range(len(entries)):
        for b in range(a + 1, len(entries)):
            (pa, ia, fa), (pb, ib, fb) = entries[a], entries[b]
            if pa == pb or ia == ib:
                continue
            if not is_glob(pa) and is_glob(pb) and matches(pa, pb):
                errors.append(f"`{pa}` ({ia}) falls inside `{pb}` ({ib}) — two phases own it")
            elif not is_glob(pb) and is_glob(pa) and matches(pb, pa):
                errors.append(f"`{pb}` ({ib}) falls inside `{pa}` ({ia}) — two phases own it")
            elif is_glob(pa) and is_glob(pb):
                sa, sb = static_prefix(pa), static_prefix(pb)
                if (sa.startswith(sb) or sb.startswith(sa)) and (matches(pa, pb) or matches(pb, pa) or sa == sb):
                    warnings.append(f"globs `{pa}` ({ia}) and `{pb}` ({ib}) may overlap — make them disjoint")

    def creator_of(path):
        for pat, pid, _ in entries:
            if pat == path or (is_glob(pat) and matches(path, pat)):
                return pid
        return None

    sharers = {}
    for p in phases:
        pid = p.get("id")
        for s in as_list(p.get("shared")):
            s = str(s)
            sharers.setdefault(s, []).append(pid)
            owner = creator_of(s)
            if owner == pid:
                warnings.append(f"{pid}: `{s}` is both owned and shared by the same phase")
            elif owner is not None:
                if owner not in ancestors(pid):
                    errors.append(f"{pid}: shares `{s}`, but its creator {owner} is not upstream of {pid}")
            elif not (root / s).exists():
                errors.append(f"{pid}: shares `{s}`, but no phase creates it and it doesn't exist yet")
    for f, ps in sorted(sharers.items()):
        if len(ps) >= 3:
            warnings.append(f"hub file `{f}` is shared by {len(ps)} phases ({', '.join(map(str, ps))}) — "
                            "they serialize; move it to one wiring phase and use registration functions")

    # -- gdd_refs
    for p in phases:
        pid, refs = p.get("id"), as_list(p.get("gdd_refs"))
        for r in refs:
            if not (root / str(r).split("#")[0]).exists():
                errors.append(f"{pid}: gdd_ref file not found: {r}")
        if not refs and p.get("kind") not in NO_REFS_OK_KINDS:
            warnings.append(f"{pid}: `{p.get('kind')}` phase cites no gdd_refs")

    # -- commands
    cmds = m.get("commands") or {}
    has_scaffold = any(p.get("kind") == "scaffold" for p in phases)
    for c in ("run", "test", "smoke", "screenshot"):
        v = str(cmds.get(c) or "").strip()
        if not v or v in ("...", '"..."'):
            errors.append(f"commands.{c} is empty")
        elif v.upper().startswith("TBD") and not has_scaffold:
            errors.append(f"commands.{c} is TBD but there is no scaffold phase to set it")
    if "{files}" not in str(cmds.get("test_one") or ""):
        warnings.append("commands.test_one should contain a {files} placeholder")
    if not cmds.get("typecheck"):
        warnings.append('commands.typecheck missing — set it, or "none" for untyped stacks')

    # -- assets
    assets = [a for a in as_list(m.get("assets")) if isinstance(a, dict)]
    aids = [a.get("id") for a in assets]
    for dup in sorted({str(i) for i in aids if aids.count(i) > 1}):
        errors.append(f"duplicate asset id `{dup}`")
    for a in assets:
        aid = a.get("id")
        if a.get("method") not in METHODS:
            errors.append(f"asset {aid}: method `{a.get('method')}` not in {sorted(METHODS)}")
        for d in as_list(a.get("depends_on")):
            if d not in aids:
                errors.append(f"asset {aid}: depends_on unknown asset `{d}`")
        owner_phase = by_id.get(a.get("phase"))
        if owner_phase is None:
            errors.append(f"asset {aid}: phase `{a.get('phase')}` not found")
        elif a.get("path") and a.get("method") != "procedural":
            path = str(a.get("path"))
            if not any(path == str(o) or (is_glob(str(o)) and matches(path, str(o)))
                       for o in as_list(owner_phase.get("owns"))):
                warnings.append(f"asset {aid}: `{path}` isn't in the `owns` of its phase {a.get('phase')}")
        if a.get("method") == "image-gen":
            warnings.append(f"asset {aid}: image-gen — confirm the user has a generation tool, and name a fallback")

    for cp in as_list(m.get("playtest_checkpoints")):
        if not isinstance(cp, dict):
            continue
        for a in as_list(cp.get("after")):
            if a not in by_id:
                errors.append(f"playtest checkpoint `{cp.get('name')}`: unknown phase `{a}`")

    # -- waves and critical path
    level = {}

    def lvl(pid, stack=()):
        if pid in level:
            return level[pid]
        if pid in stack:
            return 1
        deps = [d for d in as_list(by_id.get(pid, {}).get("depends_on")) if d in by_id]
        level[pid] = 1 + max((lvl(d, stack + (pid,)) for d in deps), default=0)
        return level[pid]

    for pid in by_id:
        lvl(pid)
    if level:
        print("Parallel waves (from depends_on):")
        for w in range(1, max(level.values()) + 1):
            members = [str(pid) for pid in by_id if level[pid] == w]
            if members:
                print(f"  wave {w}: {', '.join(members)}")
        widest = max(sum(1 for v in level.values() if v == w) for w in set(level.values()))
        end = max(level, key=level.get)
        path = [end]
        while True:
            deps = [d for d in as_list(by_id[path[-1]].get("depends_on")) if d in by_id and d not in path]
            if not deps:
                break
            path.append(max(deps, key=lambda d: level[d]))
        print(f"  widest wave: {widest} phases; critical path ({len(path)}): {' -> '.join(map(str, reversed(path)))}")
        print("  (phases that share a file can't truly overlap even within a wave)\n")

    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    owned = sum(1 for _, _, f in entries if f == "owns")
    tests = sum(1 for _, _, f in entries if f == "tests")
    print(f"\n{len(phases)} phases, {owned} owned paths, {tests} test paths, {len(assets)} assets: "
          f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
