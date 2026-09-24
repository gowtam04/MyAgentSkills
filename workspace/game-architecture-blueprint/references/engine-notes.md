# Engine Notes

Load **after** the engine is chosen. Pin typical folders and commands so the blueprint and orchestrator do not invent a layout. Adapt to the project's actual conventions when a repo already exists. This is not an engine tutorial.

Record the exact commands you pin in architecture `commands:` (override these defaults when the project uses different scripts).

## Godot (4.x)

Typical tree: `project.godot`, `scenes/`, `scripts/` or script-next-to-scene, `assets/`, `data/`, `tests/`, autoloads declared in `project.godot`.

```text
run:        godot --path . 
test:       godot --headless --path . -s addons/gut/gut_cmdln.gd -gexit
test_one:   godot --headless --path . -s addons/gut/gut_cmdln.gd -gtest={file} -gexit
export:     godot --headless --path . --export-release "{preset}" {output}
smoke:      godot --headless --path . --quit-after 2
```

Pin the export preset name (iOS, Web, …) from platform constraints. GUT or gdUnit4 — choose in Developer mode; PM infers GUT if nothing exists.

## Unity

Typical tree: `Assets/_Project/{Runtime,Tests,Art,Data}`, `ProjectSettings/`, assemblies if present.

```text
run:        # Editor: open scene. CI: Unity -batchmode -projectPath . -executeMethod {Smoke.Run}
test:       Unity -batchmode -projectPath . -runTests -testPlatform EditMode -testResults tests.xml
test_one:   Unity -batchmode -projectPath . -runTests -testFilter {name}
export:     Unity -batchmode -projectPath . -buildTarget {iOS|WebGL|...} -quit
```

Pin the bootstrap scene and which tests are EditMode vs PlayMode. PlayMode is the playtest analog when headless is available.

## Unreal

Typical tree: `Source/{Module}/`, `Content/`, `.uproject`.

Pin: module names, GameMode/Pawn ownership, `RunUAT` cook/build command for the target platform, and which tests are Automation vs functional. Prefer Blueprint-vs-C++ boundary in the file map so workers do not dual-own a Blueprint that C++ also writes.

## Web (Phaser, Pixi, Three, custom canvas)

Typical tree: `src/{scenes,systems,entities,ui}`, `public/assets/`, `index.html`, `package.json`.

```text
run:        npm run dev
test:       npm test
test_one:   npm test -- {file}
export:     npm run build
smoke:      # start dev, browser to local URL, screenshot or Playwright script named in architecture
```

If the slice is web, architecture must name the local URL and a Playwright/browser smoke path so `/game-dev-orchestrator` playtesters can exercise the loop.

## Native Apple (SpriteKit / SceneKit / custom)

Typical tree: Xcode project, `Sources/`, `Resources/`, `Tests/`.

```text
run:        xcodebuild -scheme {scheme} -destination 'platform=iOS Simulator,name={device}'
test:       xcodebuild test -scheme {scheme} -destination 'platform=iOS Simulator,name={device}'
test_one:   xcodebuild test -scheme {scheme} -only-testing:{Target/Class/method}
export:     xcodebuild -scheme {scheme} -destination generic/platform=iOS archive
```

Pin simulator name and scheme. Haptics and Game Center are platform modules with dedicated owners — not "later in UI."

## Love2D / custom native

Pin: `love .` (or the actual binary), where `main.lua` vs modules live, and how tests run (busted, etc.). If there is no test runner, architecture must say so and lean on playtest checkpoints rather than pretending TDD exists.

## Command pinning rules

- Prefer repo scripts (`package.json`, `Makefile`, `justfile`) over raw engine binaries when they exist.
- Mark `TBD — set in scaffold phase` only for greenfield scaffold; every later phase must have real commands.
- Never leave `run` blank. Orchestrator playtesters need it.
