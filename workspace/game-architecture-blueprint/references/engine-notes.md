# Engine Notes

Load **after** the engine is chosen. Pin typical folders and commands so the blueprint and orchestrator don't invent a layout. Adapt to the project's actual conventions when a repo already exists. This is not an engine tutorial.

Record the exact commands you pin in architecture `commands:` (override these defaults when the project uses different scripts).

## Why "screenshot" matters

The build is done by Claude Code subagents in a terminal. They can read logs and they can *look at PNG files* (the Read tool renders images), but they can't watch a window. So every engine section below pins a `screenshot` command that runs the game to a known state and writes images to a known path (e.g. `tmp/playtest/`). Playtesters and asset QA depend on it. If an engine can't produce a screenshot headlessly in this environment, say so in the architecture and fall back to log-based smoke checks plus a manual-playtest checkpoint for the user.

Also pin a **debug/test hook** where cheap: a way to set the RNG seed, skip menus, and read game state (e.g. `window.__game.state` on web, a `--scene` / `--seed` CLI arg in native engines). Deterministic starts make playtests repeatable.

## Web (Phaser, PixiJS, Three.js, custom canvas) — easiest for agents

Typical tree: `src/{scenes,systems,entities,ui}`, `public/assets/`, `index.html`, `package.json`, `tests/`, `scripts/`.

```text
run:        npm run dev                  # pin the local URL, e.g. http://localhost:5173
test:       npm test                     # vitest/jest for pure rules modules
test_one:   npm test -- {file}
export:     npm run build
smoke:      npx playwright test tests/smoke.spec.ts
screenshot: node scripts/screenshot.mjs  # Playwright: load URL, ?seed=1, perform core verb, save tmp/playtest/*.png
```

Keep game rules in plain TS/JS modules with no renderer imports so they're unit-testable in Node. The architecture must name the local URL and the Playwright scripts so playtesters can exercise the loop. If the user's session has a browser MCP (Playwright MCP, Claude in Chrome, or the desktop app's browser), playtesters may use it too, but the pinned script is the source of truth because it's reproducible.

## Godot (4.x)

Typical tree: `project.godot`, `scenes/`, `scripts/` or script-next-to-scene, `assets/`, `data/`, `tests/`, autoloads declared in `project.godot`.

```text
run:        godot --path .
test:       godot --headless --path . -s addons/gut/gut_cmdln.gd -gexit
test_one:   godot --headless --path . -s addons/gut/gut_cmdln.gd -gtest={file} -gexit
export:     godot --headless --path . --export-release "{preset}" {output}
smoke:      godot --headless --path . --quit-after 120
screenshot: godot --path . --write-movie tmp/playtest/frame.png --fixed-fps 30 --quit-after 90 -- --seed=1 --autoplay
```

`--headless` doesn't render, so screenshots need the normal renderer (works on a desktop session; CI needs a virtual display). Alternatively, pin a small debug script that saves `get_viewport().get_texture().get_image()` to PNG at scripted moments. Pin the export preset name from platform constraints. GUT or gdUnit4 — choose in Developer mode; PM infers GUT if nothing exists.

## Unity

Typical tree: `Assets/_Project/{Runtime,Tests,Art,Data}`, `ProjectSettings/`, assemblies if present.

```text
run:        # Editor: open bootstrap scene. CLI: Unity -batchmode -projectPath . -executeMethod {Smoke.Run}
test:       Unity -batchmode -projectPath . -runTests -testPlatform EditMode -testResults tests.xml
test_one:   Unity -batchmode -projectPath . -runTests -testFilter {name}
export:     Unity -batchmode -projectPath . -buildTarget {iOS|WebGL|...} -quit
screenshot: Unity -batchmode -projectPath . -executeMethod {Playtest.Capture} -quit   # ScreenCapture to tmp/playtest/
```

Pin the bootstrap scene and which tests are EditMode vs PlayMode. PlayMode is the playtest analog. Don't pass `-nographics` to the screenshot command. Unity needs a licensed editor on the machine — confirm that before choosing it for an agent-built project.

## Unreal

Typical tree: `Source/{Module}/`, `Content/`, `.uproject`.

Pin: module names, GameMode/Pawn ownership, `RunUAT` cook/build command, which tests are Automation vs functional, and a `HighResShot`-based capture for screenshots. Put the Blueprint-vs-C++ boundary in the file map so workers don't dual-own a Blueprint that C++ also writes. Note that agents can't author Blueprint graphs as text reliably — prefer C++ for agent-owned logic.

## Native Apple (SpriteKit / SceneKit / custom)

Typical tree: Xcode project, `Sources/`, `Resources/`, `Tests/`.

```text
run:        xcodebuild -scheme {scheme} -destination 'platform=iOS Simulator,name={device}'
test:       xcodebuild test -scheme {scheme} -destination 'platform=iOS Simulator,name={device}'
test_one:   xcodebuild test -scheme {scheme} -only-testing:{Target/Class/method}
export:     xcodebuild -scheme {scheme} -destination generic/platform=iOS archive
screenshot: xcrun simctl io booted screenshot tmp/playtest/{name}.png
```

Pin simulator name and scheme, and a launch argument that jumps to a deterministic playtest state. Haptics and Game Center are platform modules with dedicated owners — not "later in UI."

## Love2D / custom native

Pin: `love .` (or the actual binary), where `main.lua` vs modules live, how tests run (busted, etc.), and a `--screenshot` launch flag that calls `love.graphics.captureScreenshot` and quits. If there's no test runner, architecture must say so and lean on playtest checkpoints rather than pretending TDD exists.

## Command pinning rules

- Prefer repo scripts (`package.json`, `Makefile`, `justfile`) over raw engine binaries when they exist.
- Mark `TBD — set in scaffold phase` only for greenfield scaffold; every later phase must have real commands.
- Never leave `run` blank, and never leave `screenshot` blank without the explicit log-only fallback note. Orchestrator playtesters need them.
