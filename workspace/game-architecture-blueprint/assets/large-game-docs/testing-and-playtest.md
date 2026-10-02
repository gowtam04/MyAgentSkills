# Testing And Playtest

Developer mode only. Delete this file in PM mode.

## Automated Tests
Runner, where tests live, unit vs integration. What is real (time, input, RNG) vs mocked.

## What Not To Unit-Test
Feel, juice, "fun." Those are playtest checkpoints with observable criteria (readable lean, drop registers, retry in one tap).

## Playtest Scripts
Named scripts matching `playtest_checkpoints` in the manifest. First 60 seconds, core verb, fail/retry, juice moments the GDD called non-negotiable. Each script drives the game headlessly (Playwright for web, headless engine run, simulator) and saves screenshots/logs to a known path so an agent playtester can view them as evidence.

## Visual / Asset QA
The asset-artist views each produced image and writes a blind description, then compares it to the Asset Manifest row and the style lock (palette, proportions, outline, silhouette readability at game scale). Sets are compared side by side against the lock.
