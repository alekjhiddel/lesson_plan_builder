"""
IEP Writer Module — Core IEP Generation Engine
Kentucky-compliant IEP content generation for SPARK.

Generates prompts for ChatGPT following the copy/paste + process pattern.
All student data is anonymized before prompt generation.
Compliant with 707 KAR 1:320 Section 5(7) IEP content requirements.

Kentucky-specific terminology:
- ARC (Admissions & Release Committee) — NOT "IEP Team"
- EFASAA (Extended Framework for Academic and Social Achievement Assessment) — MSD students
- KAS (Kentucky Academic Standards) — LBD students
- KYECS (Kentucky Early Childhood Standards) — Preschool
- SDI (Specially Designed Instruction)
- PLAAFP (Present Levels of Academic Achievement and Functional Performance)
"""

import os
import json
from datetime import datetime, timedelta

# Path to the anonymizer in the parent SPARK app
# When integrated, this import resolves to the lesson_planner module
try:
    from modules.anonymizer import Anonymizer
except ImportError:
    # Standalone mode — minimal anonymizer for development
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lesson_planner'))
    try:
        from modules.anonymizer import Anonymizer
    except ImportError:
        # Fallback stub
        class Anonymizer:
            def __init__(self):
                self.current_mapping = {}
                self.reverse_mapping = {}

            def create_mapping(self, students):
                self.current_mapping = {}
                self.reverse_mapping = {}
                for i, s in enumerate(students, 1):
                    anon = f"Child {i}"
                    self.current_mapping[s['name']] = anon
                    self.reverse_mapping[anon] = s['name']
                return self.current_mapping

            def anonymize_student_data(self, student):
                anon_name = self.current_mapping.get(student.get('name', ''), 'Unknown Child')
                return {**student, 'name': anon_name}

            def deanonymize_text(self, text, mapping_id=None):
                for anon, real in sorted(self.reverse_mapping.items(), key=lambda x: len(x[0]), reverse=True):
                    text = text.replace(anon, real)
                return text


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
IEP_DIR = os.path.join(DATA_DIR, 'iep_documents')

# Goal domains recognized by SPARK
GOAL_DOMAINS = [
    'communication',
    'functional_life_skills',
    'academic',
    'social_emotional',
    'motor',
    'behavioral',
    'vocational_transition',
]

# Kentucky regulation reference constants
KY_REGS = {
    'iep_content': '707 KAR 1:320, Section 5(7)',
    'arc_membership': '707 KAR 1:320, Section 3',
    'transition': '707 KAR 1:320, Section 5(8)',
    'alt_assessment': '703 KAR 5:070',
    'assistive_tech': '707 KAR 1:290, Section 7',
    'least_restrictive': '707 KAR 1:350',
    'behavior_supports': '707 KAR 1:320, Section 5(3)',
    'reevaluation': '707 KAR 1:300',
    'preschool': '707 KAR 1:320, Section 10',
}


class IEPWriter:
    """Core IEP generation engine for Kentucky special education."""

    def __init__(self):
        self.anonymizer = Anonymizer()

    # ─────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────

    def generate_plaafp(self, student):
        """
        Generate a PLAAFP (Present Levels of Academic Achievement and
        Functional Performance) prompt from student dossier data.

        Per 707 KAR 1:320, Section 5(7)(a), the IEP must include:
        - How the disability affects involvement in the general curriculum
        - Current academic achievement levels
        - Current functional performance levels

        Returns: dict with 'prompt' (anonymized text for ChatGPT) and 'mapping_id'
        """
        self.anonymizer.create_mapping([student])
        anon = self.anonymizer.anonymize_student_data(student)

        prompt = self._build_plaafp_prompt(anon, student)

        return {
            'prompt': prompt,
            'prompt_type': 'plaafp',
            'student_id': student.get('id', ''),
            'mapping': self.anonymizer.current_mapping,
            'generated_at': datetime.now().isoformat(),
        }

    def generate_goals(self, student, domain):
        """
        Generate measurable IEP goals in Condition + Behavior + Criteria format.

        Per 707 KAR 1:320, Section 5(7)(b), goals must be:
        - Measurable annual goals (academic AND functional)
        - Designed to meet disability-related needs
        - Enable involvement in general curriculum

        Args:
            student: Student dossier dict
            domain: One of GOAL_DOMAINS

        Returns: dict with 'prompt' and metadata
        """
        if domain not in GOAL_DOMAINS:
            raise ValueError(f"Invalid domain '{domain}'. Must be one of: {GOAL_DOMAINS}")

        self.anonymizer.create_mapping([student])
        anon = self.anonymizer.anonymize_student_data(student)

        prompt = self._build_goals_prompt(anon, student, domain)

        return {
            'prompt': prompt,
            'prompt_type': 'goals',
            'domain': domain,
            'student_id': student.get('id', ''),
            'mapping': self.anonymizer.current_mapping,
            'generated_at': datetime.now().isoformat(),
        }

    def generate_sdi_recommendations(self, student):
        """
        Generate SDI (Specially Designed Instruction) strategy recommendations.

        References the KDE (Kentucky Department of Education) Handbook on
        SDI strategies for students with significant disabilities.

        Per 707 KAR 1:320, Section 5(7)(d): The IEP must include SDI needed
        to assist the child in advancing toward annual goals.

        Returns: dict with 'prompt' and metadata
        """
        self.anonymizer.create_mapping([student])
        anon = self.anonymizer.anonymize_student_data(student)

        prompt = self._build_sdi_prompt(anon, student)

        return {
            'prompt': prompt,
            'prompt_type': 'sdi_recommendations',
            'student_id': student.get('id', ''),
            'mapping': self.anonymizer.current_mapping,
            'generated_at': datetime.now().isoformat(),
        }

    def generate_progress_report(self, student, goal, data_points):
        """
        Generate a quarterly progress update for a specific IEP goal.

        Per 707 KAR 1:320, Section 5(7)(b)(2): Progress toward goals must
        be reported to parents at least as often as nondisabled peers receive
        report cards.

        Args:
            student: Student dossier dict
            goal: Dict with goal text, domain, criteria, baseline
            data_points: List of dicts with date, score/trial data, notes

        Returns: dict with 'prompt' and metadata
        """
        self.anonymizer.create_mapping([student])
        anon = self.anonymizer.anonymize_student_data(student)

        prompt = self._build_progress_prompt(anon, student, goal, data_points)

        return {
            'prompt': prompt,
            'prompt_type': 'progress_report',
            'student_id': student.get('id', ''),
            'goal': goal,
            'data_points_count': len(data_points),
            'mapping': self.anonymizer.current_mapping,
            'generated_at': datetime.now().isoformat(),
        }

    def generate_arc_prep(self, student):
        """
        Generate a full ARC (Admissions & Release Committee) meeting prep packet.

        Kentucky uses "ARC" per 707 KAR 1:320, Section 3. This generates:
        - PLAAFP summary
        - Goal progress across all domains
        - SDI effectiveness review
        - Recommendations for next IEP period
        - Related services summary
        - LRE justification narrative
        - Transition plan (if age 16+ per 707 KAR 1:320 Section 5(8))
        - Parent-friendly summary

        Returns: dict with 'prompt' and metadata
        """
        self.anonymizer.create_mapping([student])
        anon = self.anonymizer.anonymize_student_data(student)

        prompt = self._build_arc_prep_prompt(anon, student)

        return {
            'prompt': prompt,
            'prompt_type': 'arc_prep',
            'student_id': student.get('id', ''),
            'mapping': self.anonymizer.current_mapping,
            'generated_at': datetime.now().isoformat(),
        }

    # ─────────────────────────────────────────────────────────────────────
    # PROMPT BUILDERS (Private)
    # ─────────────────────────────────────────────────────────────────────

    def _build_plaafp_prompt(self, anon_student, raw_student):
        """Build the complete PLAAFP generation prompt."""
        disability_category = raw_student.get('disability_category', 'MSD')
        standards_ref = 'EFASAA' if disability_category == 'MSD' else 'KAS'

        prompt = f"""You are a Kentucky special education compliance expert writing a PLAAFP (Present Levels of Academic Achievement and Functional Performance) section for an IEP.

REGULATORY REQUIREMENTS (707 KAR 1:320, Section 5(7)(a)):
The PLAAFP must include:
1. A statement of the child's PRESENT LEVELS of academic achievement
2. A statement of the child's PRESENT LEVELS of functional performance
3. How the disability affects the child's involvement and progress in the general curriculum
4. For preschool children: how the disability affects participation in appropriate activities

KENTUCKY STANDARDS ALIGNMENT:
- This student participates in: {standards_ref}
- {"EFASAA (Extended Framework for Academic and Social Achievement Assessment) — aligned to Kentucky Academic Standards at reduced depth/breadth for students with moderate to severe disabilities" if disability_category == 'MSD' else "KAS (Kentucky Academic Standards) with specially designed instruction and accommodations"}

STUDENT PROFILE (anonymized):
Name: {anon_student['name']}
Age: {anon_student.get('age', 'Not specified')}
Grade: {anon_student.get('grade', 'Not specified')}
Disability Category: {disability_category}
Communication Mode: {anon_student.get('communication_mode', 'Not specified')}
Communication Details: {anon_student.get('communication_details', '')}
Cognitive Profile: {anon_student.get('cognitive_needs', 'Not specified')}
Physical Needs: {', '.join(anon_student.get('physical_needs', [])) or 'None noted'}
Behavioral Profile: {anon_student.get('behavioral_needs', 'Not specified')}
Sensory Profile: {anon_student.get('sensory_needs', 'Not specified')}
Related Services: {anon_student.get('related_services', 'None noted')}

CURRENT IEP GOALS (for context on what's been targeted):
{self._format_goals_list(anon_student.get('iep_goals', []))}

CURRENT FOCUS AREAS:
{', '.join(anon_student.get('focus_areas', [])) or 'Not specified'}

LIFE SKILLS PRIORITIES:
{', '.join(anon_student.get('life_skills_priorities', [])) or 'Not specified'}

PROGRESS NOTES:
{self._format_progress_notes(anon_student.get('progress_notes', []))}

PLEASE GENERATE A COMPLETE PLAAFP that includes:

1. **ACADEMIC ACHIEVEMENT** — Current levels across relevant domains:
   - {"Functional academics (money, time, safety words, name writing)" if disability_category == 'MSD' else "Reading, Math, Written Expression levels relative to grade-level standards"}
   - Assessment data cited (formal and informal)
   - Strengths identified alongside needs

2. **FUNCTIONAL PERFORMANCE** — Current levels in:
   - Communication (receptive and expressive)
   - Daily living / self-care skills
   - Social interaction and play skills
   - Motor skills (fine and gross)
   - Self-regulation and behavioral
   - {"Community and vocational readiness" if disability_category == 'MSD' else "Executive function and study skills"}

3. **IMPACT OF DISABILITY STATEMENT** — How the disability specifically affects:
   - Involvement in general curriculum activities
   - Progress compared to same-age peers
   - Participation in nonacademic/extracurricular activities

4. **STRENGTHS AND PREFERENCES** — What the student CAN do, enjoys, and is motivated by

5. **PARENT/GUARDIAN INPUT** — Placeholder section for family priorities and concerns

FORMAT:
- Professional narrative paragraphs (not bullet points in the final document)
- Data-referenced (use phrases like "based on classroom data," "teacher observation indicates," etc.)
- Objective, strengths-based language
- NO real names — use only the anonymized name provided
- Length: approximately 2-3 pages when printed
- End each section with a transition sentence leading to goal areas
"""
        return prompt

    def _build_goals_prompt(self, anon_student, raw_student, domain):
        """Build goal generation prompt for a specific domain."""
        disability_category = raw_student.get('disability_category', 'MSD')

        domain_descriptions = {
            'communication': 'Communication (receptive language, expressive language, pragmatics, AAC use)',
            'functional_life_skills': 'Functional/Life Skills (daily living, self-care, household, community)',
            'academic': 'Academic (reading, math, writing — functional or grade-level based on disability category)',
            'social_emotional': 'Social-Emotional (social interaction, emotional regulation, relationship skills)',
            'motor': 'Motor (fine motor, gross motor, sensory-motor, adaptive physical education)',
            'behavioral': 'Behavioral (replacement behaviors, self-regulation, coping strategies)',
            'vocational_transition': 'Vocational/Transition (work readiness, job skills, self-determination, community access)',
        }

        domain_desc = domain_descriptions.get(domain, domain)

        # Determine standards framework
        if disability_category == 'MSD':
            standards_note = """STANDARDS ALIGNMENT: EFASAA (Extended Framework for Academic and Social Achievement Assessment)
Goals should reflect functional application of Kentucky Academic Standards at significantly reduced 
depth, breadth, and complexity. Focus on generalization to real-life contexts."""
        elif raw_student.get('grade', '') in ['PK', 'Pre-K', 'Preschool']:
            standards_note = """STANDARDS ALIGNMENT: KYECS (Kentucky Early Childhood Standards)
Goals align to the five developmental domains: Adaptive, Cognitive, Communication, 
Social-Emotional, and Physical. Use age-appropriate developmental expectations."""
        else:
            standards_note = """STANDARDS ALIGNMENT: KAS (Kentucky Academic Standards)
Goals should address grade-level standards with specially designed instruction 
and accommodations to enable access and progress."""

        prompt = f"""You are a Kentucky special education IEP goal writer. Generate measurable annual goals for a student's IEP.

REGULATORY REQUIREMENTS (707 KAR 1:320, Section 5(7)(b)):
Each goal MUST be:
- Measurable (observable behavior that can be counted/measured)
- Include a CONDITION (when/given what)
- Include a BEHAVIOR (what the student will do — observable verb)
- Include CRITERIA (how well/how often — specific and measurable)
- Include a TIMELINE (by when — typically annual review date)
- Designed to meet the child's needs resulting from the disability
- Enable the child to be involved in and make progress in the general curriculum

GOAL FORMAT (Condition + Behavior + Criteria):
"Given [condition/context], [student] will [observable behavior] with [criteria for mastery] by [date]."

Example (MSD Communication):
"Given a communication board with 20+ symbols and a verbal model, Child 1 will independently select 
the correct symbol to request a desired item or activity in 8 out of 10 opportunities across 3 
consecutive data days by the annual review date."

Example (LBD Academic):
"Given grade-level text and graphic organizer support, Child 1 will identify the main idea and 
two supporting details with 80% accuracy on 4 out of 5 curriculum-based assessments by the 
annual review date."

{standards_note}

DOMAIN: {domain_desc}

STUDENT PROFILE (anonymized):
Name: {anon_student['name']}
Age: {anon_student.get('age', 'Not specified')}
Grade: {anon_student.get('grade', 'Not specified')}
Disability Category: {disability_category}
Communication Mode: {anon_student.get('communication_mode', 'Not specified')}
Cognitive Profile: {anon_student.get('cognitive_needs', 'Not specified')}
Physical Needs: {', '.join(anon_student.get('physical_needs', [])) or 'None noted'}
Behavioral Profile: {anon_student.get('behavioral_needs', 'Not specified')}
Current Focus Areas: {', '.join(anon_student.get('focus_areas', [])) or 'Not specified'}
Life Skills Priorities: {', '.join(anon_student.get('life_skills_priorities', [])) or 'Not specified'}
Reinforcers/Motivators: {anon_student.get('reinforcers', 'Not specified')}

CURRENT GOALS IN THIS DOMAIN (to build upon/replace):
{self._format_goals_for_domain(anon_student.get('iep_goals', []), domain)}

PLEASE GENERATE:

For each goal, provide:

1. **ANNUAL GOAL** — Full goal statement in Condition + Behavior + Criteria format

2. **SHORT-TERM OBJECTIVES** (2-3 benchmarks building toward the annual goal):
   - Objective 1 (achievable by first progress report)
   - Objective 2 (mid-year checkpoint)
   - Objective 3 (approaching mastery, leading to annual goal)

3. **MEASUREMENT METHOD** — How data will be collected:
   - Data collection tool (tally, +/-, duration, interval, task analysis checklist)
   - Frequency of measurement (daily, weekly, per opportunity)
   - Who collects (teacher, aide, therapist)
   - What constitutes a "trial" or "opportunity"

4. **BASELINE DATA** — Suggested baseline statement based on student profile

5. **SDI STRATEGIES** — 2-3 specially designed instruction strategies to support this goal:
   - Specific instructional methodology
   - Prompting hierarchy to use
   - Environmental supports
   - Materials/technology needed

6. **PROGRESS MONITORING SCHEDULE** — Per 707 KAR 1:320, Section 5(7)(b)(2):
   - How often progress is measured
   - How parents will be informed (at minimum, with each report card period)

Generate 2-3 goals for this domain, progressing from foundational to more complex skills.
Goals should be ambitious but achievable within one IEP year.
Use the anonymized student name only — NO real names.
"""
        return prompt

    def _build_sdi_prompt(self, anon_student, raw_student):
        """Build SDI recommendations prompt."""
        disability_category = raw_student.get('disability_category', 'MSD')

        prompt = f"""You are a Kentucky special education SDI (Specially Designed Instruction) specialist 
referencing the KDE (Kentucky Department of Education) guidance on evidence-based practices.

REGULATORY CONTEXT (707 KAR 1:320, Section 5(7)(d)):
SDI means adapting the CONTENT, METHODOLOGY, or DELIVERY of instruction to:
- Address the unique needs resulting from the child's disability
- Ensure access to the general curriculum
- Enable the child to meet educational standards

KDE HANDBOOK GUIDANCE:
SDI must be:
- Individualized to the specific student
- Based on assessment data
- Research/evidence-based
- Documented in the IEP with specificity (not vague)
- Different from what is provided to all students (general instruction)

STUDENT PROFILE (anonymized):
Name: {anon_student['name']}
Age: {anon_student.get('age', 'Not specified')}
Grade: {anon_student.get('grade', 'Not specified')}
Disability Category: {disability_category}
Communication Mode: {anon_student.get('communication_mode', 'Not specified')}
Communication Details: {anon_student.get('communication_details', '')}
Cognitive Profile: {anon_student.get('cognitive_needs', 'Not specified')}
Physical Needs: {', '.join(anon_student.get('physical_needs', [])) or 'None noted'}
Behavioral Profile: {anon_student.get('behavioral_needs', 'Not specified')}
Sensory Profile: {anon_student.get('sensory_needs', 'Not specified')}
Current SDI Notes: {anon_student.get('sdi_notes', 'None documented')}
Prompting Level: {anon_student.get('prompting_level', 'Not specified')}
Reinforcers: {anon_student.get('reinforcers', 'Not specified')}

CURRENT IEP GOALS:
{self._format_goals_list(anon_student.get('iep_goals', []))}

FOCUS AREAS:
{', '.join(anon_student.get('focus_areas', [])) or 'Not specified'}

RELATED SERVICES:
{anon_student.get('related_services', 'None noted')}

PLEASE GENERATE SDI RECOMMENDATIONS organized by category:

1. **CONTENT ADAPTATIONS** — How to modify WHAT is taught:
   - Reduced complexity/vocabulary level
   - Functional application of academic content
   - Alternative representation of concepts
   - Pre-teaching of key vocabulary/concepts

2. **METHODOLOGY ADAPTATIONS** — How to modify HOW instruction is delivered:
   - Evidence-based instructional strategies (e.g., discrete trial, task analysis, 
     systematic instruction, time delay, constant time delay, simultaneous prompting)
   - Prompting hierarchy specific to this student
   - Error correction procedures
   - Reinforcement schedule and type
   - Modeling and demonstration techniques
   - Peer-mediated strategies (if appropriate)
   - Visual supports (schedules, social stories, first-then boards)

3. **DELIVERY ADAPTATIONS** — How to modify the instructional ENVIRONMENT:
   - Setting modifications (small group, 1:1, reduced distractions)
   - Timing modifications (shorter sessions, movement breaks, pacing)
   - Sensory considerations (lighting, noise, seating)
   - Assistive technology (per 707 KAR 1:290, Section 7)
   - Communication supports (AAC, visual aids, sign language)
   - Positioning and physical access

4. **BEHAVIORAL SUPPORTS** (per 707 KAR 1:320, Section 5(3)):
   - Positive behavioral interventions
   - Antecedent strategies (prevent challenging behavior)
   - Replacement behavior teaching
   - De-escalation procedures
   - Reinforcement systems (token economy, first-then, etc.)

5. **RELATED SERVICES INTEGRATION**:
   - How SLP, OT, PT goals embed into daily instruction
   - Collaborative strategies across service providers
   - Carryover activities for classroom staff

6. **DATA COLLECTION METHODS**:
   - Simple, aide-friendly data systems
   - What to track for each SDI strategy
   - When to adjust/fade supports

For EACH recommendation, include:
- The specific strategy name
- Brief description of implementation
- Evidence base (what research supports this)
- How to document/monitor fidelity
- When to fade or modify

Write for a classroom team (teacher + aides) — clear, specific, actionable.
Use anonymized name only.
"""
        return prompt

    def _build_progress_prompt(self, anon_student, raw_student, goal, data_points):
        """Build progress report generation prompt."""

        # Format data points for the prompt
        data_summary = self._format_data_points(data_points)

        # Calculate basic statistics
        stats = self._calculate_progress_stats(data_points)

        prompt = f"""You are a Kentucky special education teacher writing a quarterly IEP progress report.

REGULATORY REQUIREMENTS (707 KAR 1:320, Section 5(7)(b)(2)):
- Progress toward annual goals must be reported to parents
- Reports must be provided at LEAST as often as report cards for nondisabled peers
- Must indicate whether progress is sufficient to meet the goal by the annual review date

PROGRESS REPORT FORMAT (Kentucky standard):
1. Goal statement (exact wording from IEP)
2. Reporting period
3. Current performance level
4. Progress rating (Mastered / Sufficient Progress / Insufficient Progress / No Progress / Regression)
5. Narrative description with data citations
6. Next steps / recommendations

STUDENT: {anon_student['name']}
DISABILITY CATEGORY: {raw_student.get('disability_category', 'MSD')}

GOAL BEING REPORTED ON:
"{goal.get('text', goal.get('goal_text', 'Goal text not provided'))}"

Domain: {goal.get('domain', 'Not specified')}
Baseline: {goal.get('baseline', 'Not documented')}
Criteria for Mastery: {goal.get('criteria', 'See goal statement')}
Goal Start Date: {goal.get('start_date', 'Beginning of IEP period')}
Annual Review Date: {goal.get('review_date', 'End of current IEP period')}

DATA COLLECTED THIS PERIOD:
{data_summary}

DATA STATISTICS:
- Number of data points: {stats['count']}
- Trend: {stats['trend']}
- Average performance: {stats['average']}
- Most recent performance: {stats['most_recent']}
- Baseline comparison: {stats['baseline_comparison']}

PLEASE GENERATE A PROGRESS REPORT that includes:

1. **PROGRESS RATING** — Select one:
   - ✅ MASTERED — Goal met; recommend new goal at ARC
   - 📈 SUFFICIENT PROGRESS — On track to meet goal by annual review
   - ⚠️ INSUFFICIENT PROGRESS — Not on track; may need ARC to revise
   - ❌ NO PROGRESS — No measurable change from baseline
   - 📉 REGRESSION — Performance has declined from baseline

2. **NARRATIVE SUMMARY** (parent-friendly language):
   - What the student is working on (plain language, not jargon)
   - What progress looks like in practical terms
   - Specific examples of what the student CAN do now
   - Data cited to support the rating
   - Comparison to baseline and criteria

3. **INSTRUCTIONAL STRATEGIES USED**:
   - What SDI has been implemented
   - What's working
   - What's been adjusted

4. **NEXT STEPS**:
   - If sufficient: continue current plan, next benchmark target
   - If insufficient: recommended modifications (SDI changes, ARC meeting)
   - If mastered: preview of what comes next

5. **PARENT COMMUNICATION NOTE**:
   - Suggested home carryover activity
   - What parents can look for at home
   - Positive framing of progress

FORMAT:
- Professional but parent-accessible language
- Data-referenced (cite specific percentages, trials, dates)
- Strengths-based — lead with what the student CAN do
- Concise — one page maximum
- Use anonymized name only
"""
        return prompt

    def _build_arc_prep_prompt(self, anon_student, raw_student):
        """Build full ARC meeting preparation packet prompt."""
        disability_category = raw_student.get('disability_category', 'MSD')
        student_age = raw_student.get('age', '')

        # Determine if transition planning required (age 16+ in Kentucky)
        needs_transition = False
        try:
            if int(student_age) >= 16:
                needs_transition = True
        except (ValueError, TypeError):
            pass

        transition_section = ""
        if needs_transition:
            transition_section = """
8. **TRANSITION PLAN** (REQUIRED — 707 KAR 1:320, Section 5(8)):
   Per Kentucky regulation, beginning no later than the IEP in effect when the child turns 16:
   - Appropriate measurable postsecondary goals (training, education, employment, independent living)
   - Based on age-appropriate transition assessments
   - Transition services needed to reach those goals
   - Course of study aligned to postsecondary goals
   - Agency linkages (OVR, CDDO, Medicaid Waiver, etc.)
   - Student invitation documentation
   - Self-determination goals
"""

        prompt = f"""You are a Kentucky special education ARC (Admissions & Release Committee) meeting preparation specialist.

IMPORTANT: In Kentucky, the IEP team is called the ARC (Admissions & Release Committee) per 707 KAR 1:320, Section 3.

ARC MEMBERSHIP REQUIREMENTS (707 KAR 1:320, Section 3):
- Parent(s) of the child
- At least one regular education teacher (if child participates in regular ed)
- At least one special education teacher
- LEA representative (qualified to provide/supervise specially designed instruction)
- Individual who can interpret evaluation results
- Others at parent or LEA discretion
- The child (when appropriate, REQUIRED for transition-age)

STUDENT: {anon_student['name']}
AGE: {anon_student.get('age', 'Not specified')}
GRADE: {anon_student.get('grade', 'Not specified')}
DISABILITY CATEGORY: {disability_category}
COMMUNICATION: {anon_student.get('communication_mode', 'Not specified')} — {anon_student.get('communication_details', '')}
COGNITIVE: {anon_student.get('cognitive_needs', 'Not specified')}
PHYSICAL: {', '.join(anon_student.get('physical_needs', [])) or 'None noted'}
BEHAVIORAL: {anon_student.get('behavioral_needs', 'Not specified')}
SENSORY: {anon_student.get('sensory_needs', 'Not specified')}
RELATED SERVICES: {anon_student.get('related_services', 'None noted')}
CURRENT SDI: {anon_student.get('sdi_notes', 'Not documented')}

CURRENT IEP GOALS:
{self._format_goals_list(anon_student.get('iep_goals', []))}

FOCUS AREAS: {', '.join(anon_student.get('focus_areas', [])) or 'Not specified'}
LIFE SKILLS PRIORITIES: {', '.join(anon_student.get('life_skills_priorities', [])) or 'Not specified'}
REINFORCERS: {anon_student.get('reinforcers', 'Not specified')}
PROMPTING LEVEL: {anon_student.get('prompting_level', 'Not specified')}

PROGRESS NOTES:
{self._format_progress_notes(anon_student.get('progress_notes', []))}

PLEASE GENERATE A COMPLETE ARC MEETING PREP PACKET:

1. **MEETING AGENDA** — Structured agenda with time allocations:
   - Welcome and introductions (roles)
   - Purpose of meeting (annual review / amendment / initial / re-evaluation)
   - Review of current PLAAFP
   - Progress report on each goal
   - Proposed goals for next IEP period
   - SDI and related services discussion
   - LRE placement discussion
   - Assessment participation (EFASAA vs. KAS)
   - {"Transition planning" if needs_transition else "Extended School Year (ESY) consideration"}
   - Parent questions and input
   - Signatures and next steps

2. **PLAAFP SUMMARY** — Condensed present levels for ARC discussion:
   - Key strengths (lead with positives)
   - Current academic levels
   - Current functional levels
   - How disability impacts general curriculum access

3. **GOAL PROGRESS SUMMARY TABLE** — For each current goal:
   - Goal area
   - Current status (Mastered / Progressing / Not Met)
   - Data snapshot
   - Recommendation (continue / revise / discontinue / new goal)

4. **PROPOSED NEW GOALS** — Draft goals for ARC consideration:
   - Based on current progress and identified needs
   - In Condition + Behavior + Criteria format
   - Across all relevant domains

5. **SDI RECOMMENDATIONS** — Current effectiveness and proposed changes:
   - What's working (continue)
   - What needs modification
   - New strategies to propose

6. **RELATED SERVICES SUMMARY**:
   - Current services, frequency, duration
   - Therapist input/recommendations
   - Proposed changes

7. **LRE JUSTIFICATION** (707 KAR 1:350):
   - Current placement and percentage of time with nondisabled peers
   - Supplementary aids and services considered
   - Why removal from general education is necessary (if applicable)
   - Continuum of alternative placements considered
{transition_section}
{"8" if not needs_transition else "9"}. **PARENT-FRIENDLY SUMMARY** — One-page overview:
   - Written at accessible reading level
   - Highlights child's growth and strengths
   - Clear explanation of what's being proposed
   - How parent can prepare questions/input
   - Parent rights reminder (procedural safeguards)

{"9" if not needs_transition else "10"}. **TEACHER PREPARATION CHECKLIST**:
   - Documents to bring
   - Data to compile
   - Work samples to gather
   - Draft IEP sections pre-written
   - Related service provider input collected
   - Prior Written Notice prepared

FORMAT:
- Professional, organized, thorough
- Data-referenced throughout
- Parent-accessible language in summary sections
- Kentucky-specific terminology (ARC, not IEP team)
- Use anonymized name only — NO real student names
- Include regulatory citations where relevant
"""
        return prompt

    # ─────────────────────────────────────────────────────────────────────
    # HELPER METHODS
    # ─────────────────────────────────────────────────────────────────────

    def _format_goals_list(self, goals):
        """Format a list of IEP goals for prompt inclusion."""
        if not goals:
            return "  No current goals documented."
        formatted = []
        for i, goal in enumerate(goals, 1):
            if isinstance(goal, dict):
                formatted.append(f"  {i}. [{goal.get('domain', 'General')}] {goal.get('text', goal.get('goal_text', str(goal)))}")
            else:
                formatted.append(f"  {i}. {goal}")
        return '\n'.join(formatted)

    def _format_goals_for_domain(self, goals, domain):
        """Format goals filtered to a specific domain."""
        if not goals:
            return "  No current goals in this domain."

        domain_goals = []
        for goal in goals:
            if isinstance(goal, dict):
                if goal.get('domain', '').lower().replace(' ', '_') == domain.lower():
                    domain_goals.append(goal.get('text', goal.get('goal_text', str(goal))))
            else:
                # String goals — include all (can't filter by domain)
                domain_goals.append(str(goal))

        if not domain_goals:
            return "  No current goals in this domain — this will be a new goal area."

        return '\n'.join(f"  • {g}" for g in domain_goals)

    def _format_progress_notes(self, notes):
        """Format progress notes for prompt inclusion."""
        if not notes:
            return "  No progress notes documented yet."
        formatted = []
        for note in notes[-10:]:  # Last 10 notes
            if isinstance(note, dict):
                formatted.append(f"  [{note.get('date', 'No date')}] {note.get('text', note.get('note', str(note)))}")
            else:
                formatted.append(f"  • {note}")
        return '\n'.join(formatted)

    def _format_data_points(self, data_points):
        """Format data points for progress report prompt."""
        if not data_points:
            return "  No formal data points collected this period."
        formatted = []
        for dp in data_points:
            date = dp.get('date', 'Unknown date')
            score = dp.get('score', dp.get('result', 'N/A'))
            trials = dp.get('trials', '')
            notes = dp.get('notes', '')
            line = f"  {date}: {score}"
            if trials:
                line += f" ({trials} trials)"
            if notes:
                line += f" — {notes}"
            formatted.append(line)
        return '\n'.join(formatted)

    def _calculate_progress_stats(self, data_points):
        """Calculate basic statistics from data points."""
        stats = {
            'count': len(data_points),
            'trend': 'Insufficient data',
            'average': 'N/A',
            'most_recent': 'N/A',
            'baseline_comparison': 'N/A',
        }

        if not data_points:
            return stats

        # Try to extract numeric scores
        scores = []
        for dp in data_points:
            score = dp.get('score', dp.get('result', None))
            if score is not None:
                try:
                    # Handle percentage strings
                    if isinstance(score, str) and '%' in score:
                        scores.append(float(score.replace('%', '')))
                    elif isinstance(score, str) and '/' in score:
                        parts = score.split('/')
                        scores.append(float(parts[0]) / float(parts[1]) * 100)
                    else:
                        scores.append(float(score))
                except (ValueError, ZeroDivisionError):
                    continue

        if scores:
            stats['average'] = f"{sum(scores) / len(scores):.1f}%"
            stats['most_recent'] = f"{scores[-1]:.1f}%"

            if len(scores) >= 3:
                first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
                second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
                if second_half > first_half + 5:
                    stats['trend'] = 'Improving (upward trend)'
                elif second_half < first_half - 5:
                    stats['trend'] = 'Declining (downward trend)'
                else:
                    stats['trend'] = 'Stable (maintaining)'
            elif len(scores) == 2:
                if scores[1] > scores[0]:
                    stats['trend'] = 'Improving'
                elif scores[1] < scores[0]:
                    stats['trend'] = 'Declining'
                else:
                    stats['trend'] = 'Stable'

            # Baseline comparison
            if len(scores) >= 2:
                change = scores[-1] - scores[0]
                stats['baseline_comparison'] = f"{'+' if change >= 0 else ''}{change:.1f}% from first data point"

        return stats

    # ─────────────────────────────────────────────────────────────────────
    # PERSISTENCE
    # ─────────────────────────────────────────────────────────────────────

    def save_generated_iep(self, iep_data):
        """Save a generated IEP document to history."""
        os.makedirs(IEP_DIR, exist_ok=True)
        filename = f"iep_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{iep_data.get('prompt_type', 'unknown')}.json"
        filepath = os.path.join(IEP_DIR, filename)
        with open(filepath, 'w') as f:
            json.dump(iep_data, f, indent=2)
        return filename

    def get_iep_history(self, student_id=None):
        """Retrieve IEP generation history, optionally filtered by student."""
        if not os.path.exists(IEP_DIR):
            return []

        history = []
        for filename in sorted(os.listdir(IEP_DIR), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(IEP_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if student_id is None or data.get('student_id') == student_id:
                            history.append({
                                'filename': filename,
                                'type': data.get('prompt_type', 'unknown'),
                                'generated_at': data.get('generated_at', ''),
                                'student_id': data.get('student_id', ''),
                                'domain': data.get('domain', ''),
                            })
                except (json.JSONDecodeError, FileNotFoundError):
                    continue

        return history
