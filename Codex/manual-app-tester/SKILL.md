---
name: manual-app-tester
description: Run local applications and manually test user-specified product scope across all applicable surfaces with the Computer Use plugin. Use when Codex is asked to manually QA, smoke test, click through, visually inspect, verify a workflow, reproduce UI behavior, or test local web, mobile, desktop, admin, or other app surfaces by actually launching and interacting with them. If the testing scope is missing, first ask the user what area, workflow, or scenario to test, then discover and test every applicable surface for that scope.
---

# Manual App Tester

## Overview

Use this workflow to run the app locally, interact with it through Computer Use, and report concrete manual QA results. Favor real UI observation over inferred behavior.

## Scope Intake

If the user did not provide a clear testing scope, ask one concise question before starting:

```text
What scope should I manually test: the feature/workflow, and any specific surfaces or device sizes you care about?
```

Proceed without another question when a reasonable scope is present. If the user does not name surfaces, inspect the project and test every surface that applies to the requested scope. Because the app is running locally, create or seed the users and data needed to test the requested scope unless the user specified exact credentials, exact fixture data, or a read-only/no-data-modification constraint.

## Workflow

1. Inspect the project enough to identify testable surfaces and how to run them locally: package scripts, README instructions, framework conventions, web apps, iOS apps, Android apps, desktop apps, admin tools, backend/admin consoles, ports, required environment variables, seed scripts, database tools, auth flows, and test fixtures.
2. Decide which surfaces apply to the user's requested scope. Include every applicable surface unless the user narrowed the scope, setup is impossible locally, or the surface is clearly unrelated.
3. Prepare local test data for the requested scope. Prefer existing seed scripts, factories, fixtures, admin/dev tools, local API endpoints, or UI signup flows. Create realistic but clearly fake users and records with deterministic names that make the test easy to follow.
4. Start each applicable app surface with the repo's normal local command. Keep servers, simulators, emulators, or desktop processes running in terminal sessions when needed, and capture the local URL, simulator, emulator, or app window used.
5. Open each applicable surface. Prefer a stable installed browser for web apps. Use available simulators/emulators for iOS and Android when present and practical.
6. Use Computer Use for manual interaction. Call `get_app_state` once before interacting with an app in each assistant turn, then use clicks, typing, key presses, scrolling, and screenshots/accessibility state to drive the test.
7. Build a compact test checklist from the user's scope for each applicable surface. Include happy path, obvious edge states, validation or error states, navigation/back behavior, empty/loading states when reachable, and responsive checks when relevant.
8. Execute the checklist manually on every applicable surface. Watch the UI, terminal logs, and visible browser/app behavior for errors, broken layout, inaccessible controls, missing feedback, stale state, crashes, or incorrect copy.
9. If a defect appears, retry the minimum path once to confirm it is reproducible before reporting it, unless retrying would modify real data or require unsafe actions.
10. Stop short of destructive production actions. Do not submit payments, send real emails/messages, delete live data, or run irreversible admin actions unless the user explicitly authorized that exact behavior.
11. Write the final QA report as a Markdown file under `docs/QA/` in the current project. Create the directory if it does not exist.

## Surface Discovery

Before testing, identify all surfaces that may exercise the requested scope:

- Web: frontend apps, marketing/app shells, admin web apps, browser extensions, responsive mobile web, and multiple browser targets when the scope depends on browser behavior.
- iOS: native iOS apps, React Native iOS targets, Expo iOS, Capacitor/Cordova iOS, or iOS simulator flows.
- Android: native Android apps, React Native Android targets, Expo Android, Capacitor/Cordova Android, or Android emulator flows.
- Desktop: Electron, Tauri, native desktop apps, menu bar apps, or installed local builds.
- Other product surfaces: CLI/TUI flows, local admin consoles, embedded widgets, browser extension popups/options pages, kiosk/TV/tablet modes, or backend-driven screens that users operate through a UI.

Use project evidence such as `package.json` scripts, workspace folders, `apps/`, `packages/`, `ios/`, `android/`, `mobile/`, `electron/`, `tauri/`, `capacitor.config.*`, `app.json`, `expo`, `xcodeproj`, `xcworkspace`, `build.gradle`, `AndroidManifest.xml`, `docker-compose.yml`, READMEs, and route names.

For each discovered surface, classify it as:

- `Tested`: applicable to the scope and successfully exercised.
- `Not applicable`: exists but the requested scope does not appear there.
- `Blocked`: applicable but could not be run or reached locally. Include the blocker and what would unblock it.

## Local Data Setup

Default to self-service local setup:

- Seed or create users/data needed for the user's scope without asking the user for credentials or fixtures.
- Use the least invasive project-native path first: documented seed commands, test fixtures, local database scripts, ORM seed utilities, dev-only admin panels, or normal signup/onboarding UI.
- Keep generated data local, fake, and scoped to the test. Use names such as `Manual QA User`, `manual-qa@example.test`, or records labeled `Manual QA`.
- If the app requires login, create a local account through signup or seed a test account. Record the created credentials in the final report only if they are fake local credentials.
- If a required external service, secret, paid integration, or production-only account blocks setup, do not ask for credentials by default. Test the reachable local behavior and report the blocker clearly.
- Ask the user for credentials or exact data only when they explicitly asked to test a specific account/dataset, local creation is impossible after reasonable discovery, or the action would touch non-local/live systems.

## Running Local Apps

Use the existing project conventions first:

- Prefer `npm run dev`, `pnpm dev`, `yarn dev`, `bun dev`, `make dev`, framework CLIs, Docker Compose, or documented commands when present.
- Install dependencies only when necessary to run the app and the repo indicates the package manager.
- If the default port is busy, use the app's supported alternate-port option or report the conflict.
- For a web app, open the captured localhost URL in the browser, then use Computer Use against that browser window.
- For an iOS app, use the repo's documented simulator workflow, Xcode workspace/project, Expo, React Native, or platform command when available.
- For an Android app, use the repo's documented emulator workflow, Gradle, Android Studio-compatible commands, Expo, React Native, or platform command when available.
- For a desktop app, launch the app normally and use Computer Use against the app window.

## Manual Testing Standards

Treat manual testing as evidence gathering:

- Interact like a real user, including keyboard navigation where it matters.
- Verify visual feedback after each important action.
- Check that loading, disabled, success, and error states are understandable.
- Resize or use available viewport controls for mobile/tablet scope when the user asks for responsive testing.
- Prefer observing the app state directly over reading source code to decide whether the UI works.
- Use source inspection only to discover run commands, routes, test accounts, feature flags, or likely paths to exercise.

## Report Artifact

Always write the final report to a scope-timestamped Markdown file in `docs/QA/`.

- Use the filename pattern `<scope-slug>-<YYYYMMDD-HHMMSS>.md`.
- Build `<scope-slug>` from the requested testing scope: lowercase, ASCII when practical, words separated by hyphens, omit filler words, and keep it short enough to scan.
- Use the local timezone unless the user specified another timezone.
- Create `docs/QA/` if it does not exist.
- Do not overwrite an existing report. If a collision happens, append a short numeric suffix.
- Include the report file path in the final chat response, plus a brief summary of the result.

Example:

```text
docs/QA/checkout-flow-20260428-153012.md
```

## Report Format

Write a concise QA report with:

- Scope tested
- Surfaces discovered and status: tested, not applicable, or blocked
- Environment: commands used, URLs/apps/devices, browser/simulator/emulator/app, seeded or created local test data
- Result summary
- Findings, ordered by severity, with reproduction steps, expected result, actual result, and evidence
- Areas not covered and why
- Server/process status if anything was left running or stopped
