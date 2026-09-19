# SPARK Feature Spec — Center-Rotation Plans (Reading / Math / Motor / SEL-Adaptive-Life-Skills)

**Version:** Draft 2.0 (rewritten with Ashley's Sep 18 answers) **Date:** September 18, 2026 **Requested by:** Ashley (teacher) **Status:** Design — ready to build via multi-agent QA pipeline

---

## The Request

Ashley's original intent:
> "Create lesson plans that go with the IEP goals each student has, group students according to similarities in those goals, and for the rest, plans that fit into center rotations divided by reading, math, motor, and social/emotional/adaptive/life skills centers."

**Clarified with Ashley (Sep 18, 2026) — the real model is a full-class center-rotation matrix:**

1. **Grouping is goal-first, then skill-based.** Where a shared IEP goal is the deciding factor, group by that goal. Where goal is NOT the deciding factor, SPARK lists the remaining kids and **asks Ashley how big to make the groups** (e.g. 6 kids → 2 groups of 3? 3 groups of 2?). Then it builds those groups by **skill level + intellectual capacity**. Grouping is interactive — SPARK proposes, Ashley sizes.
2. **Four centers are set in stone:** Reading, Math, Motor (**fine motor**), Social/Emotional/Adaptive/Life Skills. No rename/add/remove.
3. **Rotation length is customizable, defaults to 10 minutes** (typical range 10–15). Ashley can change it.
4. **ALL kids rotate through ALL four centers** on the 10–15 min schedule. Every group visits every center. **Each group gets its own activity at each center, tailored to that group per the grouping rules.** This is NOT "leftover kids only" — it is the whole class.
5. **Motor center = fine motor** (hands, pincer grasp, tracing, cutting, utensil use).

---

## The Corrected Design Model — Center × Group Matrix

The core output is a **matrix**: every center (4, fixed) × every group (N, teacher-sized) → one tailored activity per cell.

```
                READING        MATH          MOTOR(fine)    SEL/ADAPTIVE/LIFE
  Group Red  |  activity R1  | activity M1 | activity F1  | activity S1
  Group Blue |  activity R2  | activity M2 | activity F2  | activity S2
  Group Green|  activity R3  | activity M3 | activity F3  | activity S3
```

- Each cell's activity is written for that group's skill level / intellectual capacity (tiered — "same center focus, different access point").
- Every group rotates through every center (10–15 min each). The matrix IS the rotation plan.
- Theme optional (reuses existing `no_theme` / `custom_theme` plumbing). Themed = changes materials, not the skill.

---

## What Already Exists (reuse, do NOT rebuild)

| Capability | Where | Status |
| --- | --- | --- |
| IEP-goal-aligned plans (`goal_targets` per student) | `prompt_builder.py` "Build plan by goal" | DONE (v2.6.0) |
| Goal-based grouping (`group_type: "goal"`, goal tags, mid-year moves) | `group_manager.py` | DONE |
| Ability scoring (`calculate_ability_score`) + auto-cluster by skill | `group_manager.py` | DONE — reused for skill-based sizing |
| Ability grouping "same activity, different access points" prompt | `prompt_builder._build_groups_section()` | DONE |
| Generic center assignment ("Center 1/2/3") | `schedule_engine._assign_centers()` | Rewire to named centers |
| Goal `normalize_goals()` rule; blank-line goal re-split repair | `student_manager.py` | MUST honor |

---

## Part A — Fixed Four-Center Model (`center_manager.py` + `data/centers_config.json`)

Four **fixed** centers, seeded on first run. No add/remove/rename (Ashley: set in stone). Only the **rotation length** is user-editable.

```json
{
  "centers": [
    { "id": "reading", "name": "Reading Center",     "type": "reading",           "order": 1 },
    { "id": "math",    "name": "Math Center",         "type": "math",              "order": 2 },
    { "id": "motor",   "name": "Motor Center",        "type": "fine_motor",        "order": 3 },
    { "id": "sel",     "name": "Social/Emotional/Adaptive/Life Skills Center", "type": "sel_adaptive_life", "order": 4 }
  ],
  "rotation_minutes": 10
}
```

- `center_manager.py`: `get_centers()`, `get_rotation_minutes()`, `set_rotation_minutes(n)` (clamp to a sane range, e.g. 5–30; default 10). Centers list is constant — expose read-only + a `_ensure_config()` that seeds defaults and self-heals if the file is missing/corrupt.
- `type` is the stable key the prompt builder uses for center-appropriate guidance. `name`/order are display only.

---

## Part B — Grouping: Goal-First, Then Interactive Skill-Based Sizing

Two-stage grouping for the rotation:

**Stage 1 — Goal groups (automatic where a shared goal decides it).**
Reuse existing `group_type: "goal"` groups. Kids who belong to a goal group are placed by goal.

**Stage 2 — Remaining kids → interactive skill-based sizing.**
For students NOT decided by a shared goal:
1. SPARK lists the remaining kids.
2. **Asks Ashley how many groups / how big** (the UI shows the count and offers splits: e.g. 6 kids → "2 × 3", "3 × 2", "custom"). No silent auto-grouping — she sizes it.
3. SPARK then fills those groups by **skill level + intellectual capacity**, reusing `calculate_ability_score()` to sort and distribute (balanced by ability so each group is internally close in level).

Result: a full set of rotation groups (goal-decided + skill-sized), each with a clear level descriptor used to tier its activities.

---

## Part C — New `center_rotation` Plan Type (the matrix generator)

New plan type on the Generate page: **"Center Rotation Plan."**

Flow:
1. Resolve rotation groups (Part B) — goal groups + Ashley-sized skill groups.
2. For each group × each of the 4 centers → generate one tailored activity (the matrix).
3. Honor theme toggle (neutral or themed).
4. Output is para-readable, embeds data-collection + prompting level per activity (existing SPARK conventions), and honors `normalize_goals()`.

### Prompt builder changes
- New `_build_center_matrix_section(groups, centers, rotation_minutes)` — emits, per group, its level descriptor and the four centers with center-`type`-specific guidance:
  - `reading` → sight words (EXIT/STOP/name/schedule words), picture comprehension, phonological awareness at level.
  - `math` → 1:1 correspondence, counting, more/less, money, time.
  - `fine_motor` → pincer grasp, tracing, cutting, adaptive utensils, hand strength; ambulatory + adaptive access points.
  - `sel_adaptive_life` → self-regulation/coping, turn-taking/waiting/greeting, dressing/hygiene/eating routines, functional communication.
- `build_prompt(..., plan_type='center_rotation')` assembles: role, KY IEP, classroom, student profiles (grouped), the center-matrix section, schedule/theme, previous-plans + KB continuity, request. Instruct the model to return **one activity per group per center**, each tiered to the group's level.

### schedule_engine
- Replace generic "Center 1/2/3" in `_assign_centers()` with the four named centers from `center_manager` and use `get_rotation_minutes()` for timing.

### app.py routes
- Generate page: add `center_rotation` plan type; when the remaining-kids sizing step is needed, render the sizing prompt (group count/splits), collect Ashley's choice, build groups, then generate.
- `/api/centers/rotation_minutes` (GET/POST) for the customizable rotation length.

---

## Files to Modify / Add

| File | Change |
| --- | --- |
| `modules/center_manager.py` | **NEW** — fixed 4 centers + customizable rotation length (default 10) |
| `modules/group_manager.py` | Add skill-based sizing helper: given remaining students + desired group count/sizes, distribute by `calculate_ability_score()` |
| `modules/prompt_builder.py` | Add `_build_center_matrix_section()`; handle `plan_type='center_rotation'`; group resolution |
| `modules/schedule_engine.py` | Named centers + `get_rotation_minutes()` in `_assign_centers()` |
| `templates/generate.html` | "Center Rotation Plan" type; remaining-kids group-sizing step; rotation-length control |
| `templates/groups.html` | (if present) show rotation groups; else surface in generate flow |
| `app.py` | New plan type, sizing step, `/api/centers/rotation_minutes` |
| `data/centers_config.json` | **NEW** — seeded on first run (4 centers, rotation_minutes: 10) |

---

## Build Approach — Multi-Agent QA Pipeline (perfect first deploy)

Brad's standing pain point: **every prior SPARK update broke on first run and needed a second patch.** This ships through the full gate:

1. **Coder** — implements to this spec, following existing conventions (module layout, `normalize_goals()` rule, data-safety: never touch `data/` user files, seed configs idempotently).
2. **Code Reviewer** (isolated/fresh context) — correctness, edge cases, regressions, and the known SPARK traps: CodeMirror duplication on push, `normalize_goals()` before iterating goals, stale-process port-in-use, blank-line goal split.
3. **Gordon** — savage-but-substantive; worst-first, fatal-vs-nitpick; iterate until no valid criticism.
4. **Lennie** — naive-user break testing: a class with zero goal groups, 1 kid left over (can't make 2 groups), odd counts (7 kids → 2×3 + 1), a group with no ability data, rotation length set to junk, no students at all, themed vs neutral.
5. Meaning-changing decisions escalate to Brad via decision digest before merge.

**Acceptance target:** first deploy runs clean — no immediate follow-up patch.

---

## Edge Cases To Nail (from the corrected model)

- **Leftover kid** — 7 kids, Ashley picks groups of 3 → 2×3 + 1 leftover. Offer: attach to nearest-ability group, or a solo mini-group.
- **No goal groups at all** — entire class flows to Stage 2 skill sizing.
- **Everyone in goal groups** — Stage 2 skipped entirely.
- **Missing ability data** — a kid with blank `ability_level` still must be placeable (treat as unscored, surface to Ashley).
- **Rotation length** — clamp to sane bounds; reject/repair junk input; default 10.
- **Group count > students** — reject with a clear message.
- **Goals as strings vs dicts** — always `normalize_goals()` first.
