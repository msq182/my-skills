---
name: project-space-governance
description: Govern CNB-first Electron development and reduce local project storage while preserving source, runtime data, one rollback copy, and the chosen CNB/GitHub source-of-truth relationship. Use for CNB web preview, disk cleanup, duplicate project/App versions, build-artifact retention, or space-saving release workflows.
---

# Project Space Governance

Use this skill when the user wants to save disk space around a software project, clean duplicate versions, control dependencies/build artifacts, or make CNB and GitHub storage roles explicit.

## Operating modes

Choose the smallest mode that satisfies the request:

- **Inventory:** read-only size and ownership report.
- **Clean:** remove only confirmed, reproducible local artifacts.
- **Repository:** verify or establish CNB as primary and GitHub as a one-way mirror.
- **Desktop release:** build, install, and verify one current Electron App plus one rollback copy.

Do not infer a destructive cleanup, remote push, App replacement, or release publication from an inventory request.

## CNB-first Electron development

For day-to-day Electron feature work, use CNB as the default development and preview environment:

- Edit code, install dependencies, run tests, and build client/server assets in CNB.
- Use the CNB WebIDE port preview or forwarding for the running web UI; prefer the project's existing LAN-friendly dev command such as `npm run dev:lan` when available.
- Build the Electron JS bundle and other reproducible outputs in CNB, then retain only the one artifact needed for the next acceptance step.
- Do not keep local `node_modules`, `dist`, Electron download caches, `.app`, `.dmg`, or temporary preview copies merely to support routine development.
- If the CNB pipeline does not yet run the required checks or produce the needed artifact, repair or add that pipeline before shifting routine work back to the Mac.

### Standard CNB browser preview

For routine Electron UI iteration, the default acceptance path is now the CNB WebIDE browser preview:

1. Fast-forward the CNB workspace to the intended revision without overwriting a dirty checkout.
2. Run the project's preview guard when available (for FreeLLMAPI, `npm run preview:cnb`); it checks the expected ports and refuses to start over an existing process. Otherwise use `CNB_PREVIEW=1 npm run dev:lan` when the project supports its scoped preview mode, with the web server reachable on `0.0.0.0`.
3. Forward the actual web port from the WebIDE Ports panel and open the generated `*.cnb.run` URL.
4. If the forwarded host is rejected, add a narrow CNB host allowlist to the dev server and restart it; verify the forwarded URL again.
5. Visually inspect the changed route and one representative interaction, then report the exact preview URL and revision.
6. When finished, stop the foreground dev process, confirm the checkout is committed or intentionally dirty, stop/recycle the workspace, and review CNB usage. Never auto-kill an unknown process or delete a workspace containing uncommitted work.

### CNB quota guardrails

- Treat workspace runtime as the primary recurring cost: use the smallest suitable CPU configuration for routine UI preview and increase it only for a specific build or test.
- Do not leave a preview workspace running after acceptance; CNB's idle recycling is a fallback, not the completion step.
- Use the CNB usage page for periodic review. Do not invent an automatic quota API or hard-stop workflow unless the provider integration is verified and the user has approved the interruption behavior.

An empty CNB runtime database may show the first-run account setup page. That is dashboard authentication, not membership or advertising. Do not enter credentials merely to make a preview appear; add a narrowly scoped preview/demo mode only if unauthenticated preview is a confirmed product requirement.

For the detailed port-forwarding and verification procedure, use the `cnb-electron-preview` Skill when it is available.

CNB web preview is not proof of native Electron behavior. Use the Mac only when the task needs an actual macOS Electron window, menu-bar/tray behavior, native modules, macOS paths, signing, notarization, installation, or final desktop acceptance. Download or build only the current App needed for that acceptance and retain one rollback copy.

## First pass

1. Read the project `AGENTS.md` and relevant workspace instructions.
2. Run `git status --short`, `git remote -v`, and inspect the package/build scripts.
3. Run the bundled read-only inventory helper when the project has one, otherwise use `rg --files`, `du -sh`, and narrowly scoped `find` checks.
4. Classify every candidate as **source**, **runtime/user data**, **reproducible artifact**, **rollback copy**, or **unknown**. Report path, size, purpose, and proposed action before cleanup.
5. Check for secrets before any repository operation. Never print API keys, tokens, credentials, private URLs, database contents, or raw logs.

## Default storage policy

Keep:

- one active source checkout;
- one installed/current Electron App;
- one rollback App copy, retained until the new App has started and passed acceptance;
- runtime databases, SQLite WAL/SHM files, user settings, and logs unless their owner and retention rule are separately confirmed.

Regenerate on demand and do not keep in the source checkout:

- `node_modules/`;
- `client/dist/`, `server/dist/`, `cli/dist/`, desktop `build/`, staged client assets, and Electron packaging output;
- `.dmg`, `.zip`, temporary preview folders, test caches, and duplicate build copies.

Never delete or upload runtime data merely because it is large. A database, WAL, log, user-data directory, or backup requires a separate data-retention decision.

## Safe cleanup

1. Resolve exact paths first; do not use a workspace root, `$HOME`, `~`, `/`, broad globs, or unresolved variables as a destructive target.
2. Prefer moving reproducible artifacts to a clearly named Trash folder so the user can recover them.
3. For permanent deletion, present the exact paths, total size, and what is excluded, then obtain explicit confirmation immediately before deletion. If a graphical confirmation is required, keep the user's confirmation at the action point.
4. After cleanup, verify the paths are gone, measure the project again, check `git status`, and confirm the installed App and runtime data still work.
5. Do not run `git clean`, `rm -rf`, `npm audit fix`, force-push, or history rewrites as a shortcut. Use a narrow, recoverable operation or stop and explain the blocker.

## CNB and GitHub

When both remotes exist, treat `cnb` as the primary and the user's `github` remote as a one-way mirror. `upstream` is read-only unless the user explicitly says otherwise.

- Do not push during a read-only audit.
- Before a push, compare exact remote refs and verify the target history has not diverged.
- Prefer a review branch first, then fast-forward or merge to CNB `main` only when authorized.
- Verify the CNB → GitHub sync pipeline when available. If pipeline history is unavailable, state that limitation; do not force-push or overwrite divergent GitHub history.
- After publication, verify both remote `main` refs contain the intended commit and report CNB and GitHub results separately.

## Electron release

Use the Electron packaging workflow when the user asks to update or replace the installed App. Build output alone is not delivery.

1. Confirm the build target, Electron version, architecture, native modules, and version number.
2. Run tests and production builds before installation.
3. Build the `.app`, verify its signature and `Info.plist`, and note whether notarization occurred.
4. Gracefully quit the old App, preserve exactly one rollback copy, install and sign the new App, then launch it.
5. Verify the actual running process, port/window, loaded route or resource marker, and one user-visible acceptance flow.
6. Only after acceptance, remove older rollback copies and temporary build/dependency directories according to the cleanup confirmation.

If the version number is unchanged, say so clearly. A locally signed but non-notarized App is suitable for local use, not automatically for frictionless distribution.

## Verification report

Finish with a compact evidence-based report:

- paths and sizes removed or retained;
- test/build/install results and any warnings;
- current App version, process/port, and rollback path;
- CNB and GitHub commit state;
- remaining caveats, especially skipped notarization, unavailable pipeline logs, or unrun acceptance steps.

The user's current instruction overrides this policy, but does not silently broaden the targets or permissions beyond what they named.
