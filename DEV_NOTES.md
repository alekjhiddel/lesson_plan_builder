# SPARK — Developer / Maintenance Notes

Internal notes for maintaining and deploying SPARK. Not user-facing (see USER_GUIDE.md and TROUBLESHOOTING.md for those). Owner: Brad Wells (bradwell@ / alekjhiddel on GitHub).

Repo: `github.com/alekjhiddel/lesson_plan_builder` (branch: `main`)

---

## How to push code changes to GitHub (the reliable method)

There are two ways; **bulk upload is the fast, safe one** for multiple files.

### ✅ Fast path — bulk upload (use this for several files)
GitHub supports uploading multiple files in ONE commit per folder:
- Root files: `https://github.com/alekjhiddel/lesson_plan_builder/upload/main`
- Module files: `https://github.com/alekjhiddel/lesson_plan_builder/upload/main/modules`
- Templates: `https://github.com/alekjhiddel/lesson_plan_builder/upload/main/templates`

Steps: open the per-folder upload URL → choose/drag the changed files → write a commit message → "Commit directly to the main branch" → Commit. One commit per folder. This preserves folder structure and never truncates large files (e.g. `app.py`).

### ⚠️ Single-file edit path — the CodeMirror duplication trap
Editing a file in place via GitHub's web editor (`/edit/main/<path>`) uses **CodeMirror 6, which only renders VISIBLE lines** (virtualized). This caused a real production break on 2026-09-10:

- **The trap:** Selecting all with Ctrl/Cmd+A then pasting only selects the on-screen portion, so the paste **APPENDS to the off-screen remainder → the file silently DUPLICATES.** For `prompt_display.html` this produced two `{% block title %}` blocks → Jinja `TemplateAssertionError: block 'title' defined twice` → 500 on Generate.
- **The reliable clear:** focus `.cm-content`, then use a DOM Range instead of keyboard select-all:
  ```js
  const cm = document.querySelector('.cm-content');
  cm.focus();
  const sel = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(cm);      // selects the ENTIRE virtualized doc
  sel.removeAllRanges(); sel.addRange(range);
  document.execCommand('delete');    // clears it all
  ```
- **Then:** verify the editor is empty, paste the clean content, and **verify marker counts before committing** (e.g. `{% block title %}` must appear exactly once). Never commit a web-editor paste without this check.

### Committing reliably
The commit dialog's submit button text is exactly **"Commit changes"** (distinct from the **"Commit changes..."** trigger). Ensure "Commit directly to the main branch" is selected.

---

## How updates reach Ashley's machine

SPARK has a **built-in updater** (`modules/updater.py`) that checks GitHub's latest commit on `main`. It compares commit SHA (not version number), pulls `main.zip`, and preserves the `data/` folder.

**Ashley's update flow:**
1. In SPARK, click the Update button (Check for Updates) → it pulls the latest.
2. **Fully QUIT the terminal window and relaunch `start.command`.** A plain restart is not enough.

### ⚠️ The "port already in use" / stale-process trap
If a SPARK process is still running, the update downloads but the **old code keeps serving from memory** — the app looks unchanged and keeps logging old tracebacks. Tells:
- Relaunch says **"port 5000 already in use"** → an old process is still holding it.
- Terminal error logs show the **same old timestamps** as before the update → you're looking at stale output; the new code never loaded.
- **Fix:** fully quit the terminal (or reboot if the process is stuck), then relaunch so the new files load on a clean process.
- **Always check the log TIMESTAMP** to tell a stale error from a fresh one before diagnosing.

---

## Version bumping
`version.json` at repo root holds `version`, `release_date`, `changelog`. The updater works off commit SHA so a bump isn't required for updates to detect — but bump it so the in-app version label + changelog reflect the release.

---

## Data safety
- All user data (students, config, schedule, plans, ESY, mastery) lives in `data/` — **never** commit or overwrite it. The updater preserves it.
- Student names stay local and are anonymized before any external AI call (see `modules/anonymizer.py`).

---

## Known data-shape gotcha (goals)
IEP goals on a student are stored as a **list of plain strings** (from the student form), but some modules historically assumed dicts and called `goal.get(...)` → `AttributeError: 'str' object has no attribute 'get'`. Fixed via `normalize_goal()` / `normalize_goals()` in `modules/student_manager.py`, which coerce any goal (str or dict) into a consistent dict with a stable id. **Always run goals through `normalize_goals()` before iterating them** in any module.

---

_Last updated: 2026-09-10._
