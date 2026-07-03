#!/usr/bin/env bash
# recon.sh — deterministic codebase inventory for the fable-codebase-audit skill.
#
# Prints a compact, plain-text map of a repository: size, languages, top-level
# module structure, dependency manifests, test presence, secret-ish files, and
# (when it's a git repo) the churn hotspots most worth reviewing closely.
#
# The point is to spend zero model tokens on mechanical counting. Fable reads
# this output to decide how to slice the fan-out — which modules become their
# own review agents and which cross-cutting passes are needed.
#
# Usage:  bash recon.sh [REPO_PATH]     (defaults to current directory)
# Safe:   read-only. Never prints file *contents* (so secrets stay unread).

set -uo pipefail

ROOT="${1:-.}"
cd "$ROOT" 2>/dev/null || { echo "recon: cannot cd into '$ROOT'" >&2; exit 1; }
ROOT="$(pwd)"

# Directories that are never worth reviewing — vendored, generated, or VCS.
# One line on purpose: literal backslash-continuations would leak into find's
# argument list and silently match nothing.
PRUNE='-name .git -o -name node_modules -o -name vendor -o -name dist -o -name build -o -name .next -o -name .nuxt -o -name target -o -name .venv -o -name venv -o -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache -o -name coverage -o -name .terraform -o -name Pods -o -name .gradle -o -name out -o -name bin -o -name .idea -o -name .cache -o -name deps -o -name _build'

# find with the prune list applied; passes remaining args straight to find.
find_src() {
  # shellcheck disable=SC2086
  find . \( $PRUNE \) -prune -o "$@"
}

# Like find_src, but also skips binary/asset files by extension. Used for the
# LOC and largest-file passes: running `wc -l` over images/fonts/archives is
# wasteful and a single large vendored binary otherwise dominates the "largest
# files" list and pollutes the language counts. Globs are quoted so the shell
# never expands them against the cwd.
find_code() {
  # shellcheck disable=SC2086
  find . \( $PRUNE \) -prune -o \
    ! \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' \
      -o -iname '*.ico' -o -iname '*.webp' -o -iname '*.bmp' -o -iname '*.tiff' \
      -o -iname '*.pdf' -o -iname '*.zip' -o -iname '*.gz' -o -iname '*.tar' \
      -o -iname '*.tgz' -o -iname '*.bz2' -o -iname '*.7z' -o -iname '*.rar' \
      -o -iname '*.jar' -o -iname '*.war' -o -iname '*.class' -o -iname '*.wasm' \
      -o -iname '*.woff' -o -iname '*.woff2' -o -iname '*.ttf' -o -iname '*.otf' \
      -o -iname '*.eot' -o -iname '*.mp4' -o -iname '*.mov' -o -iname '*.avi' \
      -o -iname '*.mp3' -o -iname '*.wav' -o -iname '*.ogg' -o -iname '*.so' \
      -o -iname '*.dylib' -o -iname '*.dll' -o -iname '*.exe' -o -iname '*.bin' \
      -o -iname '*.o' -o -iname '*.a' -o -iname '*.pyc' \) "$@"
}

line() { printf '%s\n' "----------------------------------------------------------------------"; }

# Filter out non-source noise from ranked lists (OS cruft, lockfiles, licenses).
NOISE='\.DS_Store$|\.lock$|-lock\.json$|LICENSE|\.min\.(js|css)$|\.map$|\.svg$'

echo "======================================================================"
echo " CODEBASE RECON"
echo " root: $ROOT"
echo "======================================================================"

# ---- git context -----------------------------------------------------------
IS_GIT=no
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  IS_GIT=yes
  echo "git:            yes"
  echo "branch:         $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  echo "HEAD:           $(git log -1 --format='%h %s' 2>/dev/null)"
  echo "commits:        $(git rev-list --count HEAD 2>/dev/null)"
  echo "contributors:   $(git shortlog -sne HEAD 2>/dev/null | wc -l | tr -d ' ')"
  FIRST="$(git log --reverse --format=%as 2>/dev/null | head -1)"
  LAST="$(git log -1 --format=%as 2>/dev/null)"
  echo "history span:   ${FIRST:-?} -> ${LAST:-?}"
else
  echo "git:            no (churn hotspots unavailable)"
fi

# ---- size ------------------------------------------------------------------
line
echo "SIZE"
TOTAL_FILES=$(find_src -type f -print 2>/dev/null | wc -l | tr -d ' ')
echo "source files (excl. vendored/generated): $TOTAL_FILES"

# ---- languages by lines of code -------------------------------------------
line
echo "LANGUAGES (by lines of code, top 15)"
find_code -type f -print0 2>/dev/null \
  | xargs -0 wc -l 2>/dev/null \
  | awk '
    $2 == "total" { next }
    {
      n = split($2, p, "/"); f = p[n]
      d = match(f, /\.[^.]+$/) ? substr(f, RSTART+1) : "(none)"
      loc[d] += $1; files[d]++
    }
    END {
      for (e in loc) printf "%10d loc  %6d files  .%s\n", loc[e], files[e], e
    }' \
  | sort -rn | head -15

# ---- top-level module map --------------------------------------------------
line
echo "MODULE MAP (top-level dirs — candidate review slices)"
for d in */; do
  d="${d%/}"
  case "$d" in
    .git|node_modules|vendor|dist|build|target|.venv|venv|__pycache__|.next|.nuxt) continue;;
  esac
  fcount=$(find "./$d" \( $PRUNE \) -prune -o -type f -print 2>/dev/null | wc -l | tr -d ' ')
  loc=$(find "./$d" \( $PRUNE \) -prune -o -type f -print0 2>/dev/null \
        | xargs -0 wc -l 2>/dev/null | awk 'END{print $1+0}')
  printf "  %-28s %6s files  %8s loc\n" "$d" "$fcount" "$loc"
done
# root-level files count too
rootf=$(find . -maxdepth 1 -type f | wc -l | tr -d ' ')
printf "  %-28s %6s files\n" "(repo root files)" "$rootf"

# ---- dependency manifests --------------------------------------------------
line
echo "DEPENDENCY & BUILD MANIFESTS (supply-chain surface)"
for m in package.json package-lock.json yarn.lock pnpm-lock.yaml requirements.txt \
         Pipfile poetry.lock pyproject.toml go.mod go.sum Cargo.toml Cargo.lock \
         pom.xml build.gradle build.gradle.kts Gemfile Gemfile.lock composer.json \
         composer.lock Dockerfile docker-compose.yml .tool-versions Makefile; do
  found=$(find_src -type f -name "$m" -print 2>/dev/null | head -5)
  [ -n "$found" ] && echo "$found" | sed 's/^/  /'
done

# ---- tests & CI ------------------------------------------------------------
line
echo "TESTS & CI"
TESTS=$(find_src -type f \( -iname '*test*' -o -iname '*spec*' \) -print 2>/dev/null | wc -l | tr -d ' ')
echo "test/spec files: $TESTS"
for ci in .github/workflows .gitlab-ci.yml .circleci Jenkinsfile azure-pipelines.yml .travis.yml; do
  [ -e "$ci" ] && echo "  ci: $ci"
done

# ---- security-sensitive & secret-ish files (names only, never contents) ----
line
echo "SECRET-ISH / SENSITIVE FILES (names only — review for committed secrets)"
find_src -type f \( -name '.env*' -o -name '*.pem' -o -name '*.key' -o -name '*.pfx' \
   -o -name '*.p12' -o -name 'id_rsa*' -o -name '*credentials*' -o -name '*secret*' \
   -o -name '*.keystore' \) -print 2>/dev/null | grep -v -i example | head -30 | sed 's/^/  /'

# ---- largest source files (complexity / god-object smell) ------------------
line
echo "LARGEST SOURCE FILES (top 15 — complexity hotspots)"
find_code -type f -print0 2>/dev/null \
  | xargs -0 wc -l 2>/dev/null \
  | awk '$2 != "total"' | grep -Ev "$NOISE" | sort -rn | head -15 \
  | awk '{printf "  %8d loc  %s\n", $1, $2}'

# ---- git churn hotspots ----------------------------------------------------
if [ "$IS_GIT" = yes ]; then
  line
  echo "CHURN HOTSPOTS (most-changed files, last 1000 commits — bug-prone)"
  git log --pretty=format: --name-only -n 1000 -- . 2>/dev/null \
    | grep -v '^$' | grep -Ev "$NOISE" \
    | sort | uniq -c | sort -rn | head -15 \
    | awk '{printf "  %5d changes  %s\n", $1, $2}'
fi

line
echo "recon complete."
