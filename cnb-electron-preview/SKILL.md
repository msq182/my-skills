---
name: cnb-electron-preview
description: Preview Electron renderer changes through a CNB WebIDE workspace and forwarded browser port, with CNB-first sync, startup, visual verification, and clear separation from native macOS acceptance.
---

# CNB Electron Preview

Use this skill when the user wants to preview an Electron app, inspect the latest UI in a browser, or develop Electron features without installing local dependencies. It covers the web-renderer preview path; it does not replace native macOS packaging or installation acceptance.

## Source of truth

- Treat CNB as the primary development and preview environment when the project is configured for CNB-first work.
- Check the repository's `AGENTS.md`, `git status --short`, `git remote -v`, current branch, and package scripts before changing state.
- If CNB is primary and GitHub is a mirror, never silently reverse that relationship or force-push. A push or merge still needs explicit user authorization.
- Keep secrets, API keys, setup codes, cookies, and raw logs out of messages and artifacts.

## Preview workflow

1. Open or create the project's CNB WebIDE workspace on the intended branch. Prefer the existing workspace over creating a duplicate.
2. Synchronize the workspace with the intended remote revision using a fast-forward-only update. If the checkout is dirty, inspect it and stop before overwriting user work.
3. Run the project's preview guard when available (for FreeLLMAPI: `npm run preview:cnb`). It checks the expected server and web ports and refuses to start when either is already occupied; it never kills an existing process. If no guard exists, use `CNB_PREVIEW=1 npm run dev:lan` directly when the project supports the scoped preview mode. The web server must listen on `0.0.0.0` (or the command's equivalent), not only `127.0.0.1`.
4. Confirm the local web port from the process output or a narrow health request. Use the project's actual port; do not guess a list of ports.
5. In the WebIDE Ports panel, forward that port. Open the generated `https://<workspace>-<port>.cnb.run/` address in a browser.
6. If Vite or another dev server rejects the forwarded host, allow the CNB domain in the dev-server configuration (for Vite, use a narrow `.cnb.run` allowlist) and restart the dev server so the configuration is loaded.
7. Verify the page visually and interactively: title, primary navigation, the changed route, and one representative user flow. A `200` response alone is not visual acceptance.
8. When the preview is finished, stop the foreground dev process, confirm `git status`, and stop or recycle the CNB workspace. Do not automatically kill processes or delete a workspace with uncommitted changes.
9. Keep the preview tab open and report the exact URL, revision, forwarded port, and what was actually verified. For quota control, check the CNB usage page after unusually long sessions or at least weekly.

## Fresh workspace authentication

CNB workspaces often have a fresh runtime database. The FreeLLMAPI implementation supports `CNB_PREVIEW=1` for the forwarded `*.cnb.run` host: it reports a synthetic preview session without creating a user. The server remains read-only, blocks account changes, blocks mutations, and blocks secret-bearing reads such as the unified API key, key export, and backup downloads. If the preview shows first-run account setup, the variable is missing, the host is not a CNB forwarding host, or the server does not support this mode. Explain that the ordinary setup page is dashboard authentication, not membership or ad unlock, and that the CNB workspace does not inherit the desktop shell's hidden local session. Never invent or expose credentials. Do not disable authentication globally just to make a preview convenient.

## Storage discipline

- Install dependencies, run tests, and build reproducible client/server assets in CNB when the pipeline supports them.
- Prefer a project-provided preview guard such as `npm run preview:cnb` when available; it should check ports and set the scoped preview environment without killing processes.
- Do not create local `node_modules`, Electron download caches, `dist`, `.app`, `.dmg`, or temporary preview copies for routine UI iteration.
- Retain at most the artifact required for the next acceptance step. Treat runtime databases, SQLite WAL/SHM files, logs, user data, and one rollback copy as separate retention decisions; never delete them merely because they are large.

## Boundary: native Electron

CNB browser preview proves the renderer and its web-facing API path, not native Electron behavior. Use the Mac only for a task that needs an actual `.app`, Electron main process, tray/menu-bar behavior, native modules, macOS paths, code signing, notarization, installation, or final desktop acceptance. Build only the current native artifact needed for that acceptance and retain one rollback copy until it passes.

## Failure handling

- `403 host is not allowed`: fix the dev-server host allowlist, restart, and recheck the forwarded URL.
- `200` from the forwarded URL but a blank or stale page: inspect browser console/network state and confirm the workspace revision and dev-server restart; do not call it complete from HTTP status alone.
- Fresh setup/login page: report the authentication reason and stop before entering personal credentials unless the user explicitly asks to do so.
- Workspace countdown or recycle warning: report the remaining time and keep the source in CNB/Git; do not create a local duplicate as a workaround.

## Completion report

State separately:

- CNB workspace URL and forwarded preview URL;
- checked-out revision and branch;
- port and startup command;
- visual routes/flows verified and anything not run;
- whether native macOS acceptance remains outstanding;
- any local storage intentionally retained or avoided.
