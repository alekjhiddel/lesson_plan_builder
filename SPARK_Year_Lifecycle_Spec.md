# SPARK — Year-Over-Year Student Lifecycle

## Feature Specification v1.0

**Author:** Brad Wells**Date:** August 22, 2026**Status:** Draft — awaiting Ashley's review

---

## 1. Problem Statement

SPARK serves **all SPED teachers across the full K-12 pipeline** — from pre-school through high school transition. Unlike general education, SPED students often stay with the same teacher for multiple years and require structured handoffs between schools. The pipeline:

| Stage | Grades | Typical Duration | Transition To |
| --- | --- | --- | --- |
| **Pre-school** | Pre-K (ages 3-5) | 2-3 years | Elementary |
| **Elementary** | K-4th | 5-6 years | Middle school |
| **Middle** | 5th-8th | 3-4 years | High school |
| **High school** | 9th-12th (up to age 21 in KY) | 4-6 years | Post-secondary transition |

- Parents can choose to hold a child back — potentially multiple times at any stage
- Each year brings new IEP goals, but progress is cumulative across years
- When a student finally transitions, the receiving teacher needs a comprehensive handoff

**SPARK currently has no concept of school years.** It treats the roster as a single flat snapshot. This means:

- End-of-year progress is lost when new goals are entered
- There's no way to see multi-year growth trajectories
- No system for managing year transitions (who's staying, who's leaving, who's new)
- No concept of which "stage" a teacher operates at
- No inter-school handoff (pre-school → elementary → middle → high school)
- No handoff document generation for transitioning students

---

## 2. Design Goals

1. **Zero data loss** — closing a year archives everything; nothing is deleted
2. **Minimal friction** — year transitions should be a guided wizard, not a spreadsheet exercise
3. **Ashley-proof** — no way to accidentally wipe student history
4. **Useful for IEP meetings** — multi-year progress views are gold for annual reviews
5. **Handoff = first impression** — the receiving teacher should be able to run day-1 from the handoff report alone

---

## 3. Core Concepts

### Teacher Stage Configuration

On first setup, each teacher configures their "stage" in the pipeline:

```json
{
  "stage": "elementary",
  "grade_range": ["K", "1st", "2nd", "3rd", "4th"],
  "typical_years_with_student": 5,
  "receives_from": "pre-school",
  "transitions_to": "middle_school",
  "transition_grade": "4th",
  "school_name": "Ockerman Elementary",
  "district": "Boone County"
}

```

Stage options:

| Stage | `receives_from` | `transitions_to` | Notes |
| --- | --- | --- | --- |
| Pre-school | Early Intervention (First Steps) | Elementary | Ages 3-5; transition at K entry |
| Elementary | Pre-school | Middle school | K-4th typically |
| Middle school | Elementary | High school | 5th-8th |
| High school | Middle school | Post-secondary* | 9th-12th (or up to age 21) |

*Post-secondary transition planning is mandated starting at age 14 in Kentucky. High school SPED teachers handle transition IEP goals (employment, independent living, community). SPARK will support transition planning documentation but will ****not**** attempt to model post-school adult services (group homes, supported employment programs, etc.) — those vary too widely by county and family situation.*

### Cross-Stage Handoff Model

When a student transitions between stages (e.g., elementary → middle), the handoff includes:

1. **Outgoing teacher generates** a handoff report (comprehensive — see Section 8)
2. **Receiving teacher imports** the student via:- File transfer (USB/email — export as encrypted ZIP)

- Same-district SPARK-to-SPARK sync (if both teachers use SPARK in the same district)
- Manual re-entry (worst case — teacher types from the PDF handoff)

1. **Imported student arrives with:**- Full profile (persistent data)

- Complete year-over-year history (read-only archive from previous teacher)
- Last year's goals + progress (context for writing new IEP goals)
- Behavioral strategies that worked
- Medical/safety info

1. **Receiving teacher then:**- Sets new IEP goals for their stage

- Adjusts behavioral/physical needs if things have changed
- Begins fresh progress tracking
- Previous teacher's history remains viewable as "Prior School History"

### Export/Import Format

```
student_transfer_timmy_2027.spark
├── profile.json
├── lifecycle.json
├── handoff_report.pdf
└── history/
    ├── 2024-25.json (pre-school)
    ├── 2025-26.json (K)
    └── 2026-27.json (1st)

```

- `.spark` file = ZIP with JSON + PDFs
- Optional encryption (passphrase) for FERPA compliance during transfer
- Importing teacher sees all history as read-only "Prior School" section

---

### School Year

A bounded period (e.g., "2026–27") with its own:

- Student roster (who was active that year)
- IEP goals per student
- Progress data per goal
- Services received
- Behavioral notes
- Lesson plans generated

### Student Lifecycle States

| State | Meaning |
| --- | --- |
| `active` | Currently enrolled in Ashley's class |
| `returning` | Confirmed coming back next year |
| `held_back` | Parent chose to repeat the year (stays with Ashley, same grade) |
| `transitioning` | Aging out to next school (handoff needed) |
| `moved_away` | Left the district mid-year or between years |
| `archived` | No longer active — all years are history |

### Grade Progression

Grade progression is **stage-dependent** and configured per teacher:

| Stage | Typical Progression | Transition Trigger |
| --- | --- | --- |
| Pre-school | Pre-K Year 1 → Pre-K Year 2 → Pre-K Year 3 | Age 5 / kindergarten eligibility |
| Elementary | K → 1st → 2nd → 3rd → 4th | Completes highest grade in range |
| Middle | 5th → 6th → 7th → 8th | Completes 8th grade |
| High school | 9th → 10th → 11th → 12th (→ 13th if staying to 21) | Age 21 or graduation with modified diploma |

**Hold-back rules:** Any student can be held back at any stage. When held back:

- Grade stays the same for the repeated year
- `expected_transition_year` extends by 1
- Lifecycle history shows the repeated year clearly

**High school extension (KY-specific):** Students with IEPs can remain in school until age 21. SPARK tracks this as additional years at the "12th+" grade level, with transition planning goals becoming the primary focus after standard 12th grade.

**Post-secondary handoff:** SPARK will generate a transition summary document suitable for adult service providers, but will NOT model adult services (group homes, day programs, supported employment, Medicaid waivers) — those are too variable across counties and family situations. The handoff report covers: student's communication level, independence skills, behavioral profile, medical needs, and what educational strategies worked. The receiving adult services team takes it from there.

---

## 4. Data Model Changes

### Current Structure (flat):

```
data/
├── students/
│   ├── student_001.json     ← everything in one file
│   └── student_002.json
├── schedule_config.json
└── config.json

```

### New Structure (year-aware):

```
data/
├── current_year.json                    ← {"year": "2026-27", "started": "2026-08-12"}
├── students/
│   ├── student_001/
│   │   ├── profile.json                 ← persistent (name, DOB, diagnosis, medical, family)
│   │   ├── current_goals.json           ← this year's IEP goals + progress
│   │   ├── lifecycle.json               ← status, entry_year, grade_history, transition info
│   │   └── history/
│   │       ├── 2024-25.json             ← archived year (goals, progress, services, notes)
│   │       └── 2025-26.json
│   └── student_002/
│       ├── profile.json
│       ├── current_goals.json
│       └── lifecycle.json
├── archives/
│   ├── 2024-25/
│   │   ├── roster.json                  ← who was in the class that year
│   │   ├── schedule_config.json         ← how staffing was set up
│   │   └── year_summary.json            ← overall class metrics
│   └── 2025-26/
├── schedule_config.json
└── config.json

```

### `profile.json` (persistent across years)

```json
{
  "id": "student_001",
  "name": "Timmy",
  "dob": "2020-03-15",
  "diagnosis": "Autism Spectrum Disorder (Level 3)",
  "physical_needs": ["Wheelchair user", "G-tube fed"],
  "medical": {"allergies": ["Peanuts"], "seizure_plan": true},
  "family": {"guardian": "Mom (Sarah)", "contact": "555-0123"},
  "communication_mode": "AAC device (LAMP Words for Life)",
  "entry_year": "2024-25",
  "entry_grade": "K"
}

```

### `lifecycle.json` (tracks year-to-year state)

```json
{
  "current_status": "active",
  "current_grade": "2nd",
  "current_year": "2026-27",
  "expected_transition_year": "2028-29",
  "grade_history": [
    {"year": "2024-25", "grade": "K", "status": "completed"},
    {"year": "2025-26", "grade": "1st", "status": "completed"},
    {"year": "2026-27", "grade": "2nd", "status": "in_progress"}
  ],
  "held_back_years": [],
  "transition_notes": ""
}

```

### `current_goals.json` (this year only)

```json
{
  "year": "2026-27",
  "iep_goals": [
    {
      "id": "goal_001",
      "text": "Given a visual schedule, will independently transition between 3 activities...",
      "domain": "Independence",
      "baseline": "0/5 opportunities (Aug 2026)",
      "target": "4/5 opportunities across 3 sessions",
      "progress_data": [...],
      "mastered": false,
      "mastery_date": null
    }
  ],
  "life_skills_priorities": [...],
  "focus_areas": [...],
  "services_this_year": [...]
}

```

### Archived year file (e.g., `history/2025-26.json`)

```json
{
  "year": "2025-26",
  "grade": "1st",
  "iep_goals": [...],
  "goals_mastered": ["goal_003", "goal_005"],
  "goals_in_progress": ["goal_001", "goal_002"],
  "progress_summary": "Mastered 2/5 goals. Significant growth in AAC usage.",
  "services_received": {"SLP": 120, "OT": 60},
  "behavioral_summary": "Elopement reduced from 3x/day to 1x/week",
  "notes": "Great year. Ready for more complex requesting.",
  "archived_on": "2026-06-01"
}

```

---

## 5. Feature: End-of-Year Wrap-Up

### Trigger

- Manual: Dashboard → "Close School Year" button (appears May–July)
- Or: Settings → Year Management → Close Year

### Wizard Flow

**Step 1: Confirm Year**

> "You're closing the 2026–27 school year. This will archive all current progress data. Continue?"

**Step 2: Review Each Student**

For each active student, show:

- Name, grade, goal progress summary
- Auto-calculated status recommendation:- If grade = 4th → suggest `transitioning`
- If parent request on file → suggest `held_back`
- Otherwise → suggest `returning`
- Teacher override: Ashley can change any status

**Step 3: Year-End Notes**

For each student, optional text field:

- "Anything the next year (or next teacher) should know?"
- Pre-populated with behavioral trends, mastered goals, ongoing challenges

**Step 4: Generate Handoffs**

For students marked `transitioning`:

- Auto-generate handoff report (see Section 8)
- Option to save as PDF or print

**Step 5: Archive & Lock**

- Saves all current data to `archives/2026-27/` and `student/history/2026-27.json`
- Marks the year as closed
- Does NOT delete anything — just freezes it as read-only
- Dashboard shows: "✅ 2026–27 archived. Start 2027–28 when ready."

---

## 6. Feature: Start-of-Year Setup

### Trigger

- Dashboard → "Start New School Year" button (appears after year is closed)

### Wizard Flow

**Step 1: Confirm New Year**

> "Starting school year 2027–28. Students marked 'returning' will carry forward."

**Step 2: Returning Students**

Shows list of returning students:

- Name, new grade (auto-incremented unless held back)
- Checkbox to confirm each one
- "Remove" option if plans changed over summer

**Step 3: New Students**

- "Add new students entering your class this year"
- Same student profile form as today, but with `entry_year` auto-set

**Step 4: New IEP Goals**

For each returning student:

- Shows last year's goals (mastered ones grayed out with ✅)
- Prompt: "Enter this year's IEP goals" (likely from new IEP written over summer)
- Option to carry forward unmastered goals

**Step 5: Baseline**

- Set baseline data points for new/revised goals
- "Where is this student starting this year?"
- Progress tracking resets to zero for new goals

**Step 6: Confirm & Go**

- Creates `current_year.json` with "2027-28"
- Updates each student's `lifecycle.json` with new grade
- Fresh `current_goals.json` per student
- Dashboard refreshes with new year view

---

## 7. Feature: Multi-Year Progress View

### Where It Lives

- Student Profile → "History" tab
- Also accessible from IEP meeting prep page

### What It Shows

**Timeline View:**

```
2024-25 (K)     2025-26 (1st)     2026-27 (2nd)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AAC Requesting:  10% → 40%        40% → 75%        75% → 90% ✅ MASTERED
Transitions:     0/5 → 2/5        2/5 → 3/5        3/5 → 4/5
Handwashing:     ---- ----        0/5 → 3/5        3/5 → 5/5 ✅ MASTERED

```

**Year-over-Year Summary Card:**

```
┌─────────────────────────────────────┐
│ Timmy — 3 years in Ashley's class   │
│                                     │
│ Goals mastered total: 7             │
│ Goals active this year: 4           │
│ Services: SLP 2x/wk, OT 1x/wk     │
│ Biggest growth area: Communication  │
│ Expected transition: 2028-29        │
└─────────────────────────────────────┘

```

**Use in IEP meetings:** "Here's the 3-year trajectory showing consistent growth in requesting — now at 90%, recommend mastering this goal and replacing with a more complex communication target."

---

## 8. Feature: Handoff Report Generator

### Trigger

- End-of-Year wizard (for transitioning students)
- Manual: Student Profile → "Generate Handoff Report"
- Automatic prompt: When a student reaches their `transition_grade` SPARK surfaces "This is [name]'s last year — prepare handoff?"

### Stage-Specific Handoff Variations

The core report structure (below) is the same regardless of stage, but content emphasis shifts:

| Transition | Emphasis |
| --- | --- |
| **Pre-school → Elementary** | Sensory profile, toileting status, communication mode, separation anxiety patterns, what the preschool routine looked like |
| **Elementary → Middle** | Independence level, behavioral strategies, peer interaction patterns, which supports can fade vs which are essential |
| **Middle → High school** | Self-advocacy skills, schedule management ability, early transition planning interests, technology/AAC proficiency |
| **High school → Post-secondary** | Vocational interests/experiences, community navigation skills, independent living status, transportation capability, support level needed for employment, guardianship status |

### Report Structure

**Cover Page:**

- Student name, photo (if on file), DOB, current grade
- "Prepared by [Ashley's name] for [student]'s transition to [next school]"
- Date prepared

**Section 1: Who This Student Is**

- Diagnosis, communication mode, personality snapshot
- "What makes them light up" / reinforcers
- Family context (who picks up, who to call, dynamics)

**Section 2: What Works**

- Behavioral strategies that are effective (de-escalation, antecedents)
- Visual supports in use
- Schedule/routine needs
- Sensory profile summary

**Section 3: What to Watch For**

- Known triggers
- Medical/safety concerns (seizures, allergies, elopement)
- Behavioral patterns (time of day, seasonal, transitions)

**Section 4: Academic/IEP History**

- Multi-year goal progress (from Section 7 data)
- Current mastery levels
- Suggested next goals based on trajectory
- Related services and frequency

**Section 5: Daily Logistics**

- Transportation (bus number, aide on bus?)
- Feeding (lunch type, tube feeding, allergies)
- Toileting (schedule, assistance level, supplies)
- Communication (device, signs, PECS, verbal level)

**Section 6: What I Wish I'd Known Day 1**

- Free-text from Ashley: the real talk that doesn't fit in an IEP
- "He takes 2 weeks to warm up to new people — don't take the screaming personally"
- "Mom texts a LOT but means well — respond within 24hr and she's happy"

### Output Format

- On-screen preview (styled HTML)
- Export as PDF
- Export as DOCX
- Print-friendly version

---

## 9. Migration Plan (Existing → New Structure)

For Ashley's current students (already in SPARK with flat structure):

1. On first launch after update, run a migration:- Create `current_year.json` with the current school year

- For each existing student JSON, split into `profile.json` + `current_goals.json` + `lifecycle.json`
- Infer `entry_year` from earliest data point (or ask Ashley)
- Set all students to `active` status
- No data is lost — it's a restructure, not a delete

1. Show a one-time migration wizard:> "SPARK has been updated with year-over-year tracking! Let me set up your students for the current school year."- Confirm current year (2026–27)

- Confirm each student's grade
- Done — everything else auto-migrates

---

## 10. Implementation Phases

### Phase 1: Data Model + Migration (Foundation)

- New directory structure
- **Teacher stage configuration** (pre-school / elementary / middle / high school)
- Grade range + transition rules per stage
- Migration script (flat → year-aware)
- Migration wizard UI
- `lifecycle.json` per student
- Update all existing routes to read from new structure
- **No new features visible yet** — just the plumbing

### Phase 2: End-of-Year Wrap-Up

- Close Year wizard (5 steps)
- Archive creation
- Student status transitions
- Year-end notes capture

### Phase 3: Start-of-Year Setup

- New Year wizard
- Returning student confirmation
- New student intake (pre-filled from previous year)
- Goal entry for new year
- Baseline setting

### Phase 4: Multi-Year Progress View

- History tab on student profile
- Year-over-year goal trajectory charts
- IEP meeting prep integration
- Progress summary generation

### Phase 5: Handoff Report Generator

- Report template (6 sections)
- Auto-population from student history
- "What I wish I'd known" free-text editor
- PDF/DOCX/print export
- Preview in-app
- Stage-specific content variations (pre→elem, elem→middle, middle→HS, HS→post)

### Phase 6: Cross-Stage Transfer (SPARK-to-SPARK)

- `.spark` export format (encrypted ZIP with JSON + PDFs)
- Import wizard for receiving teacher
- "Prior School History" read-only section in student profile
- Same-district sync option (shared network folder or USB)
- FERPA-compliant transfer flow (passphrase encryption)

---

## 11. Questions for Ashley — ANSWERED ✅

| # | Question | Answer | Impact on Design |
| --- | --- | --- | --- |
| 1 | What year are we in? | 2026–27 (just started Aug 2026) | Set as initial year in migration wizard |
| 2 | How many students since K? | Not backfilling — start fresh from today | No historical import needed; simplifies Phase 1 |
| 3 | Backfill previous years? | **No** — just start tracking forward | Remove backfill UI from migration wizard |
| 4 | Current handoff process? | Transition meetings + IEP follows the kid | Handoff report = supplemental "things the IEP doesn't capture" |
| 5 | Gets handoff FROM preschool? | Yes — transition meetings with preschool teachers | Build "Intake from Previous Teacher" as optional import |
| 6 | Hold-back frequency? | Once in 7 years. Parents can hold back up to 3x total across K-12 | Low priority — build it but don't over-engineer the UX |
| 7 | What does receiving teacher want? | IEP travels with kid; transition meeting is informal | **Shift handoff report to "Transition Meeting Talking Points"** — AI-generated suggestions about things particularly unique or problematic (major special needs, safety concerns, behavioral triggers). Not a formal document — more like prep notes. |

### Key Design Implications

1. **Handoff report reframing:** NOT a formal document that replaces the IEP. Instead: AI-generated "heads-up notes" that surface things the IEP doesn't convey well — behavioral patterns, what actually works in practice, safety concerns, parent communication style. Think of it as "what you'd tell the new teacher over coffee."
2. **No backfill complexity:** Phase 1 is much simpler — just restructure current data and tag it as "2026–27". No historical import wizards.
3. **Hold-back is rare:** Keep the feature but bury it in settings. Don't put "hold back?" as a prominent choice in the end-of-year wizard — just have an override option if needed.
4. **Transition meetings are the real handoff:** Consider generating a "Transition Meeting Prep Sheet" rather than a standalone report — bullet points for Ashley to reference during the meeting, highlighting:- Things the new teacher MUST know day 1 (safety, medical, elopement risk)

- What works and what doesn't (strategies)
- Communication style with parents
- The kid's personality (what the IEP can't capture)

## 12. Technical Notes

- **Backward compatible:** If `data/students/` contains flat JSON files (old format), SPARK auto-detects and runs migration
- **No external dependencies:** All archiving is local JSON — no database needed
- **Read-only archives:** Once a year is closed, its data cannot be edited (prevents accidental corruption)
- **Export everything:** Full student history exportable as ZIP for backup or transfer
- **Multi-year progress charts:** Use the existing `calculate_progress` module, extended to read from history files

