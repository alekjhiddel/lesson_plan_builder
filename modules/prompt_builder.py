"""
Prompt Builder Module - v2
Constructs intelligent, anonymized prompts for ChatGPT.
Focused on life skills, independence, and IEP compliance for MSD classrooms.
Incorporates Kentucky-specific IEP requirements (707 KAR 1:320).
"""

import re
import os
import json
from datetime import datetime
from .group_manager import get_all_groups, get_instruction_level, calculate_ability_score
from .anonymizer import Anonymizer
from .scheduler import get_scheduling_context, get_current_themes, get_themes_for_month
from .student_manager import normalize_goals
from .center_manager import get_centers, get_rotation_minutes

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
KB_DIR = os.path.join(DATA_DIR, 'knowledge_base')
PLANS_DIR = os.path.join(DATA_DIR, 'lesson_plans')


class PromptBuilder:
    """Builds structured prompts for lesson plan generation."""
    
    def __init__(self):
        self.anonymizer = Anonymizer()
    
    def build_prompt(self, students, config, plan_type='weekly', 
                     month_override=None, custom_theme='', additional_notes='',
                     week_of=None, para_notes_style='detailed', no_theme=False,
                     goal_targets=None, rotation_groups=None):
        """
        Build a complete prompt for ChatGPT.
        Returns anonymized prompt text ready to copy/send.

        goal_targets: optional dict {student_id: [goal_index, ...]} for the
        "Build plan by goal" feature. When a student has entries, only those
        goals are shown for them and the plan is instructed to target them.
        Students not in the dict are treated normally (all goals, no targeting).
        None/empty = feature off entirely (normal plan).
        """
        # Create anonymization mapping
        self.anonymizer.create_mapping(students)
        
        # Build sections
        sections = []
        
        # 1. Role and context - LIFE SKILLS FOCUSED
        sections.append(self._build_role_section())
        
        # 2. Kentucky IEP compliance context
        sections.append(self._build_ky_iep_section())
        
        # 3. Classroom setup
        sections.append(self._build_classroom_section(config, plan_type))
        
        # 4. Student profiles (anonymized)
        sections.append(self._build_students_section(students, goal_targets))
        
        # 4b. Group context (if groups exist and plan type uses them)
        if plan_type == 'center_rotation':
            # Consume already-resolved groups from the app layer (chunk 5).
            if rotation_groups is not None:
                groups = rotation_groups
            else:
                # get_all_groups() returns ability AND goal groups; a kid can be
                # in both. DE-DUP so a student appears in at most one rotation
                # group (keep first occurrence).
                groups = []
                _seen_ids = set()
                for _g in get_all_groups():
                    _ng = dict(_g)
                    _ng['student_ids'] = [sid for sid in _g.get('student_ids', [])
                                          if not (sid in _seen_ids or _seen_ids.add(sid))]
                    groups.append(_ng)
            self._rotation_group_count = len(groups)
            matrix_section = self._build_center_matrix_section(
                groups, get_centers(), get_rotation_minutes(), students)
            if matrix_section:
                sections.append(matrix_section)
        elif plan_type in ('small_group', 'mixed'):
            groups_section = self._build_groups_section(students)
            if groups_section:
                sections.append(groups_section)
        
        # 5. Scheduling context and themes
        sections.append(self._build_schedule_section(month_override, custom_theme, no_theme))
        
        # 6. Previous plans context (for continuity)
        prev_context = self._build_previous_plans_section(month_override)
        if prev_context:
            sections.append(prev_context)
        
        # 7. Knowledge base context
        kb_context = self._build_kb_section()
        if kb_context:
            sections.append(kb_context)
        
        # 8. Specific request
        sections.append(self._build_request_section(
            plan_type, additional_notes,
            num_groups=getattr(self, '_rotation_group_count', None)))
        
        return '\n\n'.join(sections)
    
    def _build_role_section(self):
        return """You are an expert special education lesson plan designer specializing in MSD (Moderate to Severe Disabilities) self-contained classrooms for elementary students with autism and significant intellectual disabilities (IQ ≤ 55).

YOUR PHILOSOPHY - LIFE SKILLS & INDEPENDENCE FIRST:
These students are severely impacted by their disabilities. The PRIMARY goal is helping them live as independently as possible — some may avoid assisted living if they develop strong enough daily living skills. Academics are secondary to:
- Daily living skills (toileting, hygiene, dressing, eating, cooking basics)
- Communication (functional communication in ANY mode — verbal, AAC, PECS, signs)
- Social skills (turn-taking, waiting, greeting, personal space)
- Self-regulation (coping strategies, sensory management, emotional identification)
- Community skills (safety, following rules, public behavior)
- Vocational readiness (following multi-step directions, task completion, working independently)
- Functional academics (money recognition, time concepts, sight words for safety/community)

Academic content IS included but is always functional:
- Math = counting, 1:1 correspondence, money, time, more/less
- Reading = sight words (EXIT, STOP, names, schedule words), picture comprehension
- Science = cause/effect, weather for dressing, plant care
- Writing = name writing, tracing, fine motor for function

You understand:
- Evidence-based practices: discrete trial, task analysis, prompting hierarchies, visual supports
- Center-based rotation models for self-contained classrooms  
- Embedding IEP goals across multiple activities (not taught in isolation)
- The need for EXTREME repetition, routine, and predictability for this population
- Plans must be readable by paraprofessionals without verbal instruction
- Data collection must be simple and embedded naturally
- Every activity should have multiple access points (ambulatory + wheelchair, sighted + blind, verbal + non-verbal)"""
    
    def _build_ky_iep_section(self):
        return """KENTUCKY IEP COMPLIANCE (707 KAR 1:320):
When generating plans, ensure activities address IEP goals in a way that supports:
- Present Levels of Academic Achievement AND Functional Performance (PLAAFP)
- Measurable annual goals (both academic AND functional)
- The child's involvement in the general curriculum to the extent appropriate
- Specially Designed Instruction (SDI) — the specific methodology for each child
- Related services integration (speech, OT, PT goals embedded in activities)
- Progress monitoring — plans should note HOW data will be collected
- Kentucky uses "ARC" (Admissions & Release Committee) instead of "IEP team"
- Kentucky Alternate Assessment (alternate portfolio) — these students likely participate
- Assistive technology needs must be considered (707 KAR 1:290, Section 7)
- Communication needs are a SPECIAL FACTOR that must be addressed
- Behavioral needs → positive behavioral interventions and supports

IEP GOAL STRUCTURE FOR THIS POPULATION:
Goals should be:
- Observable and measurable
- Include: condition, behavior, criteria, timeline
- Example: "Given a visual schedule and verbal prompt, [Child] will independently complete 3 steps of their morning arrival routine in 4 out of 5 trials by [date]"
- Include both ACADEMIC and FUNCTIONAL goals
- Short-term objectives/benchmarks (Kentucky allows LEAs to determine use)

ACTIVITIES SHOULD ALWAYS EMBED:
- Which IEP goal(s) are being addressed
- Data collection method (tally, +/-, anecdotal, task analysis checklist)
- Prompting level expected (full physical, partial physical, model, gestural, verbal, independent)
- What "mastery" looks like for each student at each activity"""
    
    def _build_classroom_section(self, config, plan_type='weekly'):
        section = f"""CLASSROOM SETUP:
- Self-contained MSD classroom (elementary level) in Kentucky
- Number of students: {config.get('class_size', 9)}
- Staff: 1 lead teacher + {config.get('num_aides', 2)} classroom aides"""
        
        if config.get('has_floater'):
            section += """
- 1 floater aide (available for transitions, 1:1 support, homeroom escorts)
- CONSTRAINT: At least 1 aide must remain in the classroom AT ALL TIMES (safety)"""
        
        # MAJOR-1: one source of truth for rotation facts. For center_rotation the
        # group count & rotation length come from the matrix / get_rotation_minutes(),
        # so do NOT hard-code "3 groups rotating every 15-20 minutes" here.
        if plan_type == 'center_rotation':
            section += """
- Center rotation model: groups rotate through the fixed centers (group count and rotation length are specified in the Center-Rotation Matrix below)"""
        else:
            section += """
- Center rotation model: 3 groups rotating every 15-20 minutes"""

        section += """
- Students rotate to general education homeroom on individual schedules (details below)
- When an aide escorts a student to homeroom, remaining staff must cover the room
- Related service providers (SLP, OT, PT) may push in during centers

DAILY STRUCTURE PRIORITIES:
1. Predictable routine (same structure every day, visual schedule)
2. Life skills embedded throughout (arrival routine, snack prep, cleanup, dismissal)
3. Center rotations for targeted instruction
4. 1:1 aide time for intensive IEP goal work
5. Sensory breaks and movement as NEEDED (not just scheduled)
6. Community-based instruction opportunities when possible"""
        
        return section
    
    def _build_students_section(self, students, goal_targets=None):
        section = "STUDENT PROFILES (anonymized for privacy):\n"
        goal_targets = goal_targets or {}
        any_targeting = False
        
        for student in students:
            anon = self.anonymizer.anonymize_student_data(student)
            section += f"\n--- {anon['name']} ---\n"
            section += f"Age: {anon['age']}, Grade: {anon['grade']}\n"
            
            if anon['communication_mode']:
                section += f"Communication: {anon['communication_mode']}"
                if anon['communication_details']:
                    section += f" ({anon['communication_details']})"
                section += "\n"
            
            if anon['cognitive_needs']:
                section += f"Cognitive Profile: {anon['cognitive_needs']}\n"
            
            if anon['physical_needs']:
                section += f"Physical Needs: {', '.join(anon['physical_needs'])}\n"
            
            if anon.get('behavioral_needs'):
                section += f"Behavioral: {anon['behavioral_needs']}\n"
            
            if anon.get('sensory_needs'):
                section += f"Sensory: {anon['sensory_needs']}\n"
            
            if anon.get('reinforcers'):
                section += f"Motivators/Reinforcers: {anon['reinforcers']}\n"
            
            # "Build plan by goal": if this student has selected goal indices,
            # show ONLY those goals and flag them as the targeted focus.
            sid = student.get('id', '')
            targeted_idx = goal_targets.get(sid)
            # PRIVACY + FORMAT FIX: goals may be stored as dicts ({'text': ...})
            # or strings. Emitting the raw item leaked the real name inside the
            # goal text (dict repr) straight into the prompt. Mirror the matrix
            # builder: normalize_goals() to clean text, then scrub THIS student's
            # own name to their label first, then a global scrub so any peer
            # names mentioned are anonymized too.
            _label = anon['name']
            def _scrub_own(text, _student=student):
                _lab = anon['name']
                result = text
                local = {_student.get('name', ''): _lab}
                for tok in (_student.get('name', '') or '').split():
                    core = tok[:-1] if tok.endswith('.') else tok
                    if len(core) >= 2 and re.fullmatch(r"[A-Za-z]+([-\'][A-Za-z]+)*", core):
                        local.setdefault(core, _lab)
                for nm in sorted((k for k in local if k), key=len, reverse=True):
                    result = re.sub(r"\b" + re.escape(nm) + r"\b", local[nm],
                                    result, flags=re.IGNORECASE)
                return self.anonymizer.anonymize_text(result, students)
            _norm = normalize_goals(student.get('iep_goals'))
            goals_texts = []
            for _g in _norm:
                _t = _g.get('text', '')
                if _t:
                    goals_texts.append(_scrub_own(_t))
            if goals_texts:
                if targeted_idx:
                    any_targeting = True
                    chosen = [g for i, g in enumerate(goals_texts) if i in set(targeted_idx)]
                    if not chosen:  # indices didn't line up — fall back to all
                        chosen = list(goals_texts)
                    section += "IEP Goals — 🎯 TARGET THESE GOALS for this student's plan:\n"
                    for goal in chosen:
                        section += f"  • {goal}\n"
                else:
                    section += "IEP Goals:\n"
                    for goal in goals_texts:
                        section += f"  • {goal}\n"
            
            if anon.get('related_services'):
                section += f"Related Services: {anon['related_services']}\n"
            
            if anon['focus_areas']:
                section += f"Current Focus: {', '.join(anon['focus_areas'])}\n"
            
            # Homeroom info
            if anon['homeroom_attends']:
                section += f"Homeroom: YES - {anon['homeroom_duration']}"
                if anon['homeroom_aide_accompanies']:
                    section += " (aide accompanies)"
                else:
                    section += " (goes independently)"
                if anon['homeroom_schedule']:
                    section += f" Schedule: {anon['homeroom_schedule']}"
                section += "\n"
            else:
                section += "Homeroom: Does not attend general education homeroom\n"
        
        if any_targeting:
            section += ("\n🎯 TARGETED-GOALS MODE: For any student whose goals are marked "
                        "\"TARGET THESE GOALS\", build that student's activities to directly work "
                        "those specific goals — every activity should map to one of them. Students "
                        "shown with a normal \"IEP Goals\" list have no targeting; plan for them as "
                        "usual across their goals.\n")

        return section
    

    def _build_center_matrix_section(self, groups, centers, rotation_minutes, students):
        """Build the Center x Group rotation matrix section.

        Emits, per group, anonymized members AND each member's anonymized IEP
        goal texts, then the 4 fixed centers, and instructs the model to produce
        ONE tailored activity per group per center (N x 4 total).
        """
        all_students = students or []

        # FATAL-1: only bail if there are NO centers AND NO students.
        if not centers and not all_students:
            return ""

        student_by_id = {}
        anon_name_by_id = {}
        for student in all_students:
            sid = student.get('id')
            student_by_id[sid] = student
            anon_name_by_id[sid] = self.anonymizer.anonymize_student_data(student)['name']

        import re as _re

        def _scrub_goal_text(student, label, text):
            """Scrub a member's own goal text.

            M1 fix: the global anonymizer maps a shared first name to whichever
            student was seen FIRST, so a goal that names its own child (e.g.
            "Ava will count") could be mis-attributed to a different Child N
            when two kids share a first name. Replace THIS student's own name
            tokens with THIS student's label first, then run the global scrub
            so any peer names mentioned are still anonymized (privacy).
            """
            result = text
            local = {student.get('name', ''): label}
            for tok in (student.get('name', '') or '').split():
                core = tok[:-1] if tok.endswith('.') else tok
                if len(core) >= 2 and _re.fullmatch(r"[A-Za-z]+([-\'][A-Za-z]+)*", core):
                    local.setdefault(core, label)
            for nm in sorted((k for k in local if k), key=len, reverse=True):
                result = _re.sub(r"\b" + _re.escape(nm) + r"\b", local[nm],
                                 result, flags=_re.IGNORECASE)
            # global scrub catches any OTHER students' names in the text
            return self.anonymizer.anonymize_text(result, all_students)

        def _member_block(student):
            sid = student.get('id')
            label = anon_name_by_id.get(sid, '(unknown student - not in this plan)')
            header = f"  - {label}"
            # m1: surface an unscored/unassessed student rather than silently tiering them.
            ability = student.get('ability_level') or {}
            if not any(ability.get(k) for k in ('functional_level', 'communication_tier',
                                                'independence_tier', 'academic_access')):
                header += " (ability not yet assessed - confirm tier with teacher)"
            lines = [header + ":"]
            goals = normalize_goals(student.get('iep_goals'))
            emitted = False
            for goal in goals:
                raw = goal.get('text', '')
                if not raw:
                    continue
                text = _scrub_goal_text(student, label, raw)
                lines.append(f"      \u2022 Goal: {text}")
                emitted = True
            if not emitted:
                lines.append("      \u2022 (no IEP goals on file - target functional priorities)")
            return "\n".join(lines)

        fallback_whole_class = False
        if not groups:
            fallback_whole_class = True
            groups = [{
                'name': 'Whole Class',
                'description': '',
                'student_ids': [s.get('id') for s in all_students],
            }]

        section = "CENTER-ROTATION MATRIX (FULL CLASS):\n"
        section += (
            f"The class runs a 4-center rotation. ALL groups rotate through ALL "
            f"four centers, spending {rotation_minutes} minutes at each center. "
            "Every group visits every center; each group gets its OWN activity at "
            "each center, tailored to that group's level (same center focus, "
            "different access point).\n\n"
        )
        if fallback_whole_class:
            section += (
                "NOTE: No groups have been sized yet. Treat the WHOLE CLASS as ONE "
                "group at each center for now, tiering each activity to the range of "
                "learners listed below.\n\n"
            )

        section += "GROUPS (rotate through every center):\n"
        # NOTE: no cross-group de-dup here. In goal-based grouping a student
        # legitimately belongs to MULTIPLE groups (e.g. Math-Identifying AND
        # Math-Recognizing), so every group must render its FULL membership.
        # De-dup for the get_all_groups() fallback lives in build_prompt (where a
        # kid could otherwise appear in both an ability and a goal group); this
        # builder renders whatever groups it is handed, overlap preserved.
        for group in groups:
            name = self.anonymizer.anonymize_text(group.get('name', 'Group') or 'Group', all_students)
            member_students = []
            for sid in group.get('student_ids', []):
                st = student_by_id.get(sid)
                if st is None:
                    member_students.append({'id': sid, 'name': '__missing__', 'iep_goals': []})
                else:
                    member_students.append(st)

            section += f"\nGroup {name}"
            if member_students:
                n = len(member_students)
                section += f" ({n} student{'s' if n != 1 else ''})"
            section += ":\n"

            if group.get('instruction_level'):
                lvl = self.anonymizer.anonymize_text(str(group['instruction_level']), all_students)
                section += f"  Level: {lvl}\n"
            if group.get('avg_score') is not None and group.get('avg_score') != '':
                # avg_score should be numeric; render defensively and scrub if somehow free-text.
                avg_raw = group['avg_score']
                if isinstance(avg_raw, (int, float)):
                    section += f"  Avg ability score: {avg_raw}\n"
                else:
                    section += f"  Avg ability score: {self.anonymizer.anonymize_text(str(avg_raw), all_students)}\n"
            desc = group.get('description')
            if desc:
                section += f"  Description: {self.anonymizer.anonymize_text(desc, all_students)}\n"
            if group.get('goal_tags'):
                tags = [self.anonymizer.anonymize_text(str(t), all_students) for t in group['goal_tags']]
                section += f"  Shared goal focus: {', '.join(tags)}\n"

            section += "  Members & IEP goals:\n"
            for st in member_students:
                if st.get('name') == '__missing__':
                    section += "    - (unknown student - not in this plan)\n"
                    continue
                section += _member_block(st) + "\n"

        CENTER_GUIDANCE = {
            'reading': (
                "Sight words (EXIT, STOP, name, schedule words), picture "
                "comprehension, and phonological awareness AT THE GROUP'S LEVEL."
            ),
            'math': (
                "1:1 correspondence, counting, more/less, money recognition, "
                "and time concepts."
            ),
            'fine_motor': (
                "Pincer grasp, tracing, cutting, adaptive utensils, and hand "
                "strength. Provide BOTH ambulatory and adaptive access points."
            ),
            'sel_adaptive_life': (
                "Self-regulation/coping strategies, turn-taking/waiting/greeting, "
                "dressing/hygiene/eating routines, and functional communication."
            ),
        }

        section += "\nTHE 4 FIXED CENTERS (each group gets a tailored activity at each):\n"
        for center in (centers or []):
            cname = center.get('name', center.get('id', 'Center'))
            ctype = center.get('type', '')
            guidance = CENTER_GUIDANCE.get(ctype, "Functional, life-skills-focused activity at the group's level.")
            section += f"  - {cname} [{ctype}]: {guidance}\n"

        section += (
            "\nPRODUCE THE MATRIX: For EACH group \u00d7 EACH center, write ONE activity "
            "(one activity per group per center). Keep the same center focus across "
            "groups but tier each activity to that group's level with a different "
            "access point, and target the specific IEP goals listed for that group's "
            "members. Every activity must be PARA-READABLE (an aide can run it "
            "without verbal instruction) and must embed BOTH the data-collection "
            "method (tally, +/-, task-analysis checklist, anecdotal) AND the expected "
            "prompting level (full physical, partial physical, model, gestural, "
            "verbal, independent).\n"
        )

        return section
    def _build_groups_section(self, students):
        """Build the ability/goal group context for the prompt."""
        all_groups = get_all_groups()
        if not all_groups:
            return ""
        
        # Build a student lookup by ID (using anonymized names)
        student_lookup = {}
        for student in students:
            anon = self.anonymizer.anonymize_student_data(student)
            student_lookup[student['id']] = {
                'anon_name': anon['name'],
                'student': student
            }
        
        section = "ABILITY GROUPS:\n"
        section += "(Students are grouped by similar functional levels for differentiated instruction)\n\n"
        
        # Ability groups first
        ability_groups = [g for g in all_groups if g.get('group_type') == 'ability']
        for group in ability_groups:
            member_count = 0
            member_lines = []
            scores = []
            
            for sid in group.get('student_ids', []):
                if sid in student_lookup:
                    info = student_lookup[sid]
                    student = info['student']
                    ability = student.get('ability_level', {})
                    score = calculate_ability_score(student)
                    scores.append(score)
                    
                    func = ability.get('functional_level', 'unknown')
                    comm = ability.get('communication_tier', 'unknown')
                    indep = ability.get('independence_tier', 'unknown')
                    acad = ability.get('academic_access', 'unknown')
                    
                    member_lines.append(
                        f"  - {info['anon_name']}: {func} functional, "
                        f"{comm}, {indep} prompting, {acad} access"
                    )
                    member_count += 1
            
            if member_count == 0:
                continue
            
            avg_score = sum(scores) / len(scores) if scores else 0
            instruction = get_instruction_level(avg_score)
            
            section += f"Group {group['name']} ({member_count} students):\n"
            section += '\n'.join(member_lines) + '\n'
            section += f"  GROUP INSTRUCTION LEVEL: {instruction}\n\n"
        
        # Goal groups
        goal_groups = [g for g in all_groups if g.get('group_type') == 'goal']
        if goal_groups:
            section += "\nGOAL-BASED GROUPS:\n"
            section += "(Students grouped by shared IEP goal areas)\n\n"
            
            for group in goal_groups:
                members = [student_lookup[sid]['anon_name'] 
                          for sid in group.get('student_ids', [])
                          if sid in student_lookup]
                if not members:
                    continue
                
                tags = ', '.join(group.get('goal_tags', []))
                section += f"Group {group['name']} — {tags} ({len(members)} students):\n"
                section += f"  Members: {', '.join(members)}\n"
                if group.get('description'):
                    section += f"  Focus: {group['description']}\n"
                section += '\n'
        
        section += """IMPORTANT: Within each group, every child must have a meaningful role. The activity
should challenge the highest-ability child in the group WITHOUT leaving the lowest-ability
child unable to participate. Use tiered task analysis — same activity, different access points.\n"""
        
        return section
    
    def _build_schedule_section(self, month_override=None, custom_theme='', no_theme=False):
        context = get_scheduling_context()

        # "No theme" — teacher opted out of seasonal theming for this plan.
        # Strip the suggested-theme / theme-color lines from the context so the
        # AI doesn't run with them (e.g. "everything is apples"), and give an
        # explicit instruction to keep materials theme-neutral. A custom theme,
        # if also provided, still wins (explicit request overrides opt-out).
        if no_theme and not custom_theme:
            kept = [ln for ln in context.split('\n')
                    if not ln.strip().startswith(('- Suggested Themes:', '- Theme Colors:', '- Activity Ideas:'))]
            context = '\n'.join(kept)
            context += ("\nNO SEASONAL THEME: The teacher has turned OFF seasonal/monthly theming for this plan. "
                        "Do NOT apply a seasonal or holiday theme (no apples, pumpkins, snowmen, etc.). "
                        "Keep materials and visuals neutral and functional. Focus purely on the IEP goals and skills.\n")
            return context

        if month_override:
            themes = get_themes_for_month(month_override)
            context += f"\nOVERRIDE - Planning for: {themes['month']}\n"
            context += f"Themes: {', '.join(themes['themes'])}\n"
        
        if custom_theme:
            context += f"\nTEACHER-REQUESTED THEME: {custom_theme}\n"
            context += "Incorporate this theme into materials/visuals but NOT at the expense of IEP goals.\n"
            context += "The theme changes the MATERIALS, not the underlying SKILLS being taught.\n"
        
        return context
    
    def _build_previous_plans_section(self, month_override=None):
        """Look at previous lesson plans for continuity and year-over-year reuse."""
        if not os.path.exists(PLANS_DIR):
            return ""
        
        plans = []
        target_month = month_override or datetime.now().month
        
        for filename in sorted(os.listdir(PLANS_DIR), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(PLANS_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        plan = json.load(f)
                        plans.append(plan)
                except:
                    continue
        
        if not plans:
            return ""
        
        section = "PREVIOUS PLANS CONTEXT (for continuity):\n"
        
        # Last plan (avoid repetition)
        if plans:
            last = plans[0]
            section += f"\nMost recent plan ({last.get('generated_at', 'unknown')[:10]}):\n"
            # Include a brief summary
            raw = last.get('raw_response', last.get('processed', ''))
            if raw:
                section += f"Summary of last plan (first 300 chars): {raw[:300]}...\n"
                section += "IMPORTANT: Avoid repeating the same specific activities. Build on progress. Introduce slight variations.\n"
        
        # Same month last year (for seasonal reuse)
        year_ago_plans = []
        current_year = datetime.now().year
        for plan in plans:
            gen_date = plan.get('generated_at', '')
            if gen_date:
                try:
                    plan_date = datetime.fromisoformat(gen_date)
                    if plan_date.year == current_year - 1 and plan_date.month == target_month:
                        year_ago_plans.append(plan)
                except:
                    continue
        
        if year_ago_plans:
            section += f"\nSAME MONTH LAST YEAR ({len(year_ago_plans)} plan(s) found):\n"
            section += "You may reuse successful themes/activities from last year with modifications.\n"
            for p in year_ago_plans[:2]:
                raw = p.get('raw_response', p.get('processed', ''))
                if raw:
                    section += f"Previous: {raw[:200]}...\n"
        
        return section
    
    def _build_kb_section(self):
        """Include relevant knowledge base summaries."""
        if not os.path.exists(KB_DIR):
            return ""
        
        resources = []
        for filename in os.listdir(KB_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(KB_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        resource = json.load(f)
                        if resource.get('summary'):
                            resources.append(resource['summary'])
                except:
                    continue
        
        if not resources:
            return ""
        
        section = "REFERENCE KNOWLEDGE (from teacher-curated resources):\n"
        for i, summary in enumerate(resources[:5], 1):
            section += f"\n[Resource {i}]: {summary[:500]}\n"
        
        return section
    
    def _build_request_section(self, plan_type, additional_notes='', num_groups=None):
        if plan_type == 'weekly':
            request_text = """PLEASE GENERATE:

1. **WEEKLY CLASSROOM PLAN** — A complete week (Monday-Friday) including:
   - Daily whole-group activities (morning meeting, closing circle, story time)
   - Center rotation assignments (which group at which center, 3 rotations × 15-20 min)
   - Staff assignments (who runs which center, who covers what)
   - Life skills embedded throughout (arrival routine, snack prep, cleanup, transitions)
   - Themed materials list for the week
   - Embedded IEP goal tracking opportunities at EVERY activity
   - Data collection reminders
   - Homeroom rotation schedule (which child goes when, which aide escorts)
   - Sensory break options built into the schedule
   
2. **DAILY INDIVIDUAL PLANS** — For each child, for each day (Monday-Friday):
   These are for 1:1 AIDE TIME — detailed enough that an aide can follow without verbal instruction:
   
   For each child's daily plan include:
   - **IEP Goal(s) targeted** (list the specific goal being worked on)
   - **Objective for this session** (what does success look like today?)
   - **Materials needed** (be specific — the aide needs to prep)
   - **Setup** (how to arrange the space/materials)
   - **Procedure** (step-by-step, numbered, simple language):
     * Include prompting hierarchy (what level of help to provide)
     * Include error correction procedure
     * Include what to do between trials/steps
   - **Data collection** (exactly what to record — tally sheet? +/-? time?)
   - **Reinforcement** (what motivates THIS child, how often to reinforce)
   - **If struggling** (backup plan — simpler version, sensory break, switch activity)
   - **Generalization note** (how this skill connects to real life)
   
   VARIETY: Don't repeat the same activity every day. Target the same GOAL but through different activities/materials across the week.

FORMAT:
- Clear headers, bullet points, numbered steps
- PRINT-FRIENDLY (an aide should be able to print their page and go)
- No education jargon — write for someone without a teaching degree
- Include a Monday materials prep list (everything needed for the whole week)
- Staff assignment grid showing who is where, every time block"""
        
        elif plan_type == 'daily_individual':
            request_text = """PLEASE GENERATE:

**DAILY INDIVIDUAL LESSON PLANS** for 1:1 aide instructional time.

For EACH child, create a detailed plan that covers:
- **Target IEP Goal** (copy the exact goal wording)
- **Today's Activity** (specific, engaging, themed if possible)
- **Materials** (exact list — aide needs to gather these)
- **Step-by-step procedure** (numbered, simple language):
  1. Setup (arrange materials, position student)
  2. Instruction (exact words to say, how to present)
  3. Student response (what you're looking for)
  4. Consequence (reinforce correct / correct errors)
  5. Repeat or move to next step
- **Prompting** (start with [level] prompt, fade to [level])
- **Data** (record: +/- for each trial, OR tally, OR duration)
- **Reinforcement schedule** (every trial? every 3? end of session?)
- **Backup plan** (if student is dysregulated or refusing)
- **Connection to life** (why this skill matters for independence)

FORMAT:
- ONE page per student per day
- Large text, simple language, no jargon
- An aide with no special education training should understand this completely"""
        
        elif plan_type == 'small_group':
            request_text = """PLEASE GENERATE:

**SMALL GROUP LESSON PLANS** for each ability group listed above.

For EACH GROUP, create a plan that includes:
- **Group name and members**
- **Shared activity** (one activity the whole group does together)
- **Tiered task analysis** — for each student in the group:
  * Their specific role/task level within the activity
  * Prompting level expected
  * What "success" looks like for THIS student
  * Data collection target
- **Materials** (what's needed, noting any student-specific adaptations)
- **Setup and procedure** (step-by-step, written for an aide)
- **IEP goals addressed** per student
- **Backup plan** if a student is struggling

Remember: SAME activity, DIFFERENT access points. Every child participates meaningfully."""
        
        elif plan_type == 'mixed':
            request_text = """PLEASE GENERATE:

**MIXED FORMAT LESSON PLANS** combining:
1. **Whole-class activities** (morning meeting, closing circle, group cooking/art)
2. **Small group plans** for each ability group (centers, targeted instruction)
3. **Individual 1:1 plans** for each student's aide time

Use the ability groups listed above to differentiate the small-group portions.
Whole-class activities should be accessible to ALL students with tiered participation.
Individual plans target each student's specific IEP goals.

FORMAT: Organize by time block — show who is where, doing what, with whom."""
        
        elif plan_type == 'center_rotation':
            n = num_groups if isinstance(num_groups, int) and num_groups > 0 else None
            if n:
                for_phrase = f"for EACH of the {n} groups listed above"
                count_phrase = f"{n} \u00d7 4 activities total"
            else:
                for_phrase = "for EACH group listed above"
                count_phrase = "one activity per group per center (groups \u00d7 4 centers)"
            request_text = (
                "PLEASE GENERATE:\n\n"
                "**FULL CENTER \u00d7 GROUP ROTATION MATRIX**\n\n"
                f"Produce the full Center \u00d7 Group matrix: {for_phrase}, ONE tailored "
                f"activity at EACH of the 4 centers = {count_phrase}. Do NOT write one "
                "shared activity per center; every group needs its OWN tiered activity "
                "at every center, targeting that group's members' IEP goals.\n\n"
                "For EACH cell (group \u00d7 center) include:\n"
                "- **Activity** (tiered to the group's level; same center focus, different access point)\n"
                "- **IEP goal(s) targeted** for that group's members\n"
                "- **Step-by-step procedure** (PARA-READABLE - an aide runs it without verbal instruction)\n"
                "- **Prompting level** (full physical, partial physical, model, gestural, verbal, independent)\n"
                "- **Data collection** (tally, +/-, task-analysis checklist, anecdotal)\n\n"
                "FORMAT: Present as a matrix/grid organized by group, then by center."
            )
        
        else:
            request_text = f"""PLEASE GENERATE a {plan_type} lesson plan following the classroom structure and IEP integration described above."""
        
        if additional_notes:
            request_text += f"\n\nADDITIONAL TEACHER NOTES:\n{additional_notes}"
        
        return request_text
    
    def get_mapping(self):
        """Return current anonymization mapping for reference."""
        return self.anonymizer.get_current_mapping()