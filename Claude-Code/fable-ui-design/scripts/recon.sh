#!/usr/bin/env bash
# fable-ui-design recon — read-only. Answers: what is this app, how do I run it,
# what are the screens, and does it already have design tokens?
# Usage: bash recon.sh [repo-path]   (defaults to current dir)
set -uo pipefail

ROOT="${1:-.}"
cd "$ROOT" 2>/dev/null || { echo "Cannot cd into $ROOT"; exit 1; }

sec() { printf '\n=== %s ===\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

# Prefer ripgrep; fall back to grep -r. `f <pattern> [path]`
if have rg; then f() { rg -l --hidden -g '!node_modules' -g '!.git' "$1" "${2:-.}" 2>/dev/null | head -40; }
else f() { grep -rlI --exclude-dir=node_modules --exclude-dir=.git "$1" "${2:-.}" 2>/dev/null | head -40; }
fi

sec "PLATFORM & STACK"
PLATFORM="unknown"
if [ -f package.json ]; then
  DEPS="$(cat package.json 2>/dev/null)"
  echo "package.json found."
  case "$DEPS" in
    *'"next"'*)          PLATFORM="web (Next.js)";;
    *'"react-native"'*)  PLATFORM="mobile (React Native)";;
    *'"expo"'*)          PLATFORM="mobile (Expo/React Native)";;
    *'"@remix-run'*)     PLATFORM="web (Remix)";;
    *'"nuxt"'*)          PLATFORM="web (Nuxt/Vue)";;
    *'"@angular/core"'*) PLATFORM="web (Angular)";;
    *'"svelte"'*)        PLATFORM="web (Svelte)";;
    *'"vite"'*)          PLATFORM="web (Vite)";;
    *'"react-scripts"'*) PLATFORM="web (Create React App)";;
    *'"electron"'*)      PLATFORM="desktop (Electron)";;
    *'"vue"'*)           PLATFORM="web (Vue)";;
    *'"react"'*)         PLATFORM="web (React)";;
  esac
fi
[ -f pubspec.yaml ]                        && PLATFORM="mobile (Flutter)"
ls *.xcodeproj *.xcworkspace >/dev/null 2>&1 && PLATFORM="native iOS (Xcode)"
[ -f build.gradle ] || [ -f app/build.gradle ] && [ "$PLATFORM" = "unknown" ] && PLATFORM="native Android (Gradle)"
echo "Detected platform: $PLATFORM"

sec "HOW TO RUN IT (dev/start scripts)"
if [ -f package.json ] && have node; then
  node -e 'try{const s=require("./package.json").scripts||{};for(const k of Object.keys(s)){if(/^(dev|start|serve|storybook|ios|android|web)$/.test(k))console.log("  npm run "+k+"  ->  "+s[k])}}catch(e){}' 2>/dev/null
elif [ -f package.json ]; then
  echo "  (node not available to parse scripts; inspect package.json 'scripts' manually)"
fi
[ -f pubspec.yaml ] && echo "  flutter run"
ls *.xcodeproj *.xcworkspace >/dev/null 2>&1 && echo "  open in Xcode / xcodebuild + simulator"
echo "  If nothing above runs cleanly, fall back to reading source or ask for screenshots."

sec "SCREENS / ROUTES (best-effort — verify by reading)"
# Next.js app router / pages router
for d in app src/app pages src/pages; do
  if [ -d "$d" ]; then
    echo "-- $d (Next.js routing):"
    find "$d" -maxdepth 4 \( -name 'page.*' -o -name 'index.*' -o -name '*.tsx' -o -name '*.jsx' \) 2>/dev/null \
      | grep -viE '/(components|_|api)/' | head -40 | sed 's/^/    /'
  fi
done
# Conventional screens/pages/views/routes directories
for d in $(find . -type d \( -name screens -o -name views -o -name routes \) -not -path '*/node_modules/*' 2>/dev/null | head -10); do
  echo "-- $d:"
  find "$d" -maxdepth 2 \( -name '*.tsx' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' -o -name '*.dart' -o -name '*.swift' \) 2>/dev/null | head -30 | sed 's/^/    /'
done
# React Router / route declarations
echo "-- files declaring routes (Route/createBrowserRouter/router):"
f 'createBrowserRouter|<Route |path:.*element:|useRoutes' | sed 's/^/    /'

sec "EXISTING DESIGN TOKENS / THEME (what's already decided)"
for cfg in tailwind.config.js tailwind.config.ts tailwind.config.cjs theme.js theme.ts theme.json \
           src/theme.ts src/styles/theme.ts app/globals.css src/index.css src/App.css styles/globals.css; do
  [ -f "$cfg" ] && echo "  token/theme file: $cfg"
done
echo "-- CSS custom properties (:root variables) — count of files:"
f -- '--[a-z].*:' 2>/dev/null | wc -l | tr -d ' ' | sed 's/^/    files defining CSS vars: /'
echo "-- UI component library in use:"
if [ -f package.json ]; then
  for lib in '@mui/material' 'antd' 'react-bootstrap' 'bootstrap' 'chakra' '@radix-ui' 'shadcn' 'tailwindcss' 'styled-components' 'emotion' 'nativewind' 'react-native-paper'; do
    grep -q "\"$lib" package.json 2>/dev/null && echo "    - $lib"
  done
fi
echo "-- animation/motion libraries (does motion already exist?):"
if [ -f package.json ]; then
  for lib in 'framer-motion' 'motion' 'react-spring' 'gsap' 'react-native-reanimated' '@react-spring' 'auto-animate' 'lottie'; do
    grep -q "\"$lib" package.json 2>/dev/null && echo "    - $lib"
  done
fi

sec "SCALE"
echo "  frontend source files (approx):"
find . -type f \( -name '*.tsx' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' -o -name '*.dart' -o -name '*.swift' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ' | sed 's/^/    /'

sec "RECON DONE"
echo "Next: pick how to SEE the UI (screenshots if runnable, else source, else ask),"
echo "then delegate capture/inventory to subagents and look at the screens yourself."
