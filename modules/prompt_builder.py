"""
Prompt Builder Module - v2
Constructs intelligent, anonymized prompts for ChatGPT.
Focused on life skills, independence, and IEP compliance for MSD classrooms.
Incorporates Kentucky-specific IEP requirements (707 KAR 1:320).
"""

import os
import json
from datetime import datetime
from .anonymizer import Anonymizer
from .scheduler import get_scheduling_context, get_current_themes, get_themes_for_month
from .student_manager import get_all_students

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
KB_DIR = os.path.join(DATA_DIR, 'knowledge_base')
PLANS_DIR = os.path.join(DATA_DIR, 'lesson_plans')


class PromptBuilder:
    """Builds structured prompts for lesson plan generation."""
    
    def __init__(self):
        self.anonymizer = Anonymizer()
    
    def build_prompt(self, students, config, plan_type='weekly', 
                     month_override=None, custom_theme='', additional_notes='',
                     week_of=None, para_notes_style='detailed'):
        """
        Build a complete prompt for ChatGPT.
        Returns anonymized prompt text ready to copy/send.
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
        sections.append(self._build_classroom_section(config))
        
        # 4. Student profiles (anonymized)
        sections.append(self._build_students_section(students))
        
        # 5. Scheduling context and themes
        sections.append(self._build_schedule_section(month_override, custom_theme))
        
        # 6. Previous plans context (for continuity)
        prev_context = self._build_previous_plans_section(month_override)
        if prev_context:
            sections.append(prev_context)
        
        # 7. Knowledge base context
        kb_context = self._build_kb_section()
        if kb_context:
            sections.append(kb_context)
        
        # 8. Specific request
        sections.append(self._build_request_section(plan_type, additional_notes))
        
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
    
    def _build_classroom_section(self, config):
        section = f"""CLASSROOM SETUP:
- Self-contained MSD classroom (elementary level) in Kentucky
- Number of students: {config.get('class_size', 9)}
- Staff: 1 lead teacher + {config.get('num_aides', 2)} classroom aides"""
        
        if config.get('has_floater'):
            section += """
- 1 floater aide (available for transitions, 1:1 support, homeroom escorts)
- CONSTRAINT: At least 1 aide must remain in the classroom AT ALL TIMES (safety)"""
        
        section += """
- Center rotation model: 3 groups rotating every 15-20 minutes
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
    
    def _build_students_section(self, students):
        section = "STUDENT PROFILES (anonymized for privacy):\n"
        
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
            
            if anon['iep_goals']:
                section += "IEP Goals:\n"
                for goal in anon['iep_goals']:
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
        
        return section
    
    def _build_schedule_section(self, month_override=None, custom_theme=''):
        context = get_scheduling_context()
        
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
    
    def _build_request_section(self, plan_type, additional_notes=''):
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
        
        else:
            request_text = f"""PLEASE GENERATE a {plan_type} lesson plan following the classroom structure and IEP integration described above."""
        
        if additional_notes:
            request_text += f"\n\nADDITIONAL TEACHER NOTES:\n{additional_notes}"
        
        return request_text
    
    def get_mapping(self):
        """Return current anonymization mapping for reference."""
        return self.anonymizer.get_current_mapping()
