"""
SPARK - Parent Communications Module
Generates warm, professional communications for special education families.

Communication Types:
- Progress letters (formal IEP progress updates)
- Daily backpack logs (quick daily communication)
- Behavior updates (incident-specific)
- Celebration notes (positive achievement sharing)
- Conference prep (talking points for parent-teacher meetings)

NOTE: These communications include real student names because they are
printed locally and sent home in backpack folders. They do NOT go through
any AI/cloud service. If a teacher wants AI assistance drafting, the
anonymize_for_ai() function strips PII before prompting.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
import re


# ─────────────────────────────────────────────────────────────────────
# TONE CONFIGURATIONS
# ─────────────────────────────────────────────────────────────────────

TONE_SETTINGS = {
    'professional': {
        'greeting': 'Dear {parent_name}',
        'closing': 'Sincerely',
        'style': 'formal',
        'description': 'Formal and respectful, suitable for official updates'
    },
    'warm': {
        'greeting': 'Hi {parent_name}',
        'closing': 'Warmly',
        'style': 'friendly',
        'description': 'Friendly and approachable, good for daily communication'
    },
    'positive': {
        'greeting': 'Dear {parent_name}',
        'closing': 'With appreciation',
        'style': 'encouraging',
        'description': 'Upbeat and encouraging, highlights growth'
    },
    'concerned': {
        'greeting': 'Dear {parent_name}',
        'closing': 'Thank you for your partnership',
        'style': 'supportive',
        'description': 'Caring but direct, for behavior or concern discussions'
    }
}


# ─────────────────────────────────────────────────────────────────────
# ANONYMIZATION (for optional AI-assisted drafting)
# ─────────────────────────────────────────────────────────────────────

def anonymize_for_ai(text: str, student: dict) -> str:
    """
    Strip PII from text before sending to any AI/cloud service.
    Replaces real names with generic placeholders.
    
    Args:
        text: The communication text to anonymize
        student: Student dict containing name info
        
    Returns:
        Anonymized text safe for AI prompting
    """
    anonymized = text
    
    # Replace student names
    first_name = student.get('first_name', '')
    last_name = student.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    
    if full_name:
        anonymized = anonymized.replace(full_name, '[STUDENT]')
    if first_name:
        anonymized = anonymized.replace(first_name, '[STUDENT]')
    if last_name:
        anonymized = anonymized.replace(last_name, '[LAST_NAME]')
    
    # Replace parent names
    parent_name = student.get('parent_name', '')
    if parent_name:
        anonymized = anonymized.replace(parent_name, '[PARENT]')
    
    # Replace school name if present
    school = student.get('school', '')
    if school:
        anonymized = anonymized.replace(school, '[SCHOOL]')
    
    # Replace teacher name
    teacher = student.get('teacher_name', '')
    if teacher:
        anonymized = anonymized.replace(teacher, '[TEACHER]')
    
    return anonymized


def deanonymize_from_ai(text: str, student: dict, teacher_name: str = '') -> str:
    """
    Replace placeholders back with real names after AI drafting.
    
    Args:
        text: AI-generated text with placeholders
        student: Student dict with real names
        teacher_name: Teacher's name to insert
        
    Returns:
        Text with real names restored
    """
    result = text
    result = result.replace('[STUDENT]', student.get('first_name', 'your child'))
    result = result.replace('[LAST_NAME]', student.get('last_name', ''))
    result = result.replace('[PARENT]', student.get('parent_name', 'Family'))
    result = result.replace('[SCHOOL]', student.get('school', 'our school'))
    result = result.replace('[TEACHER]', teacher_name or 'your teacher')
    return result


# ─────────────────────────────────────────────────────────────────────
# PROGRESS LETTER
# ─────────────────────────────────────────────────────────────────────

def generate_progress_letter(student: dict, period: str, tone: str = 'positive',
                             teacher_name: str = '', school_name: str = '') -> dict:
    """
    Generate a formal progress update letter referencing IEP goals.
    
    Args:
        student: Student dict with keys:
            - first_name, last_name, parent_name
            - iep_goals: list of goal dicts with {area, goal, baseline, current, target, status}
            - grade, classroom, disability_category
        period: Reporting period (e.g., "Q1 2024", "January Progress Report")
        tone: One of 'professional', 'warm', 'positive', 'concerned'
        teacher_name: Teacher's name for signature
        school_name: School name for header
        
    Returns:
        dict with 'subject', 'body', 'metadata'
    """
    tone_config = TONE_SETTINGS.get(tone, TONE_SETTINGS['positive'])
    parent_name = student.get('parent_name', 'Family')
    first_name = student.get('first_name', 'your child')
    
    greeting = tone_config['greeting'].format(parent_name=parent_name)
    
    # Build IEP goal progress section
    goals_section = _format_goals_progress(student.get('iep_goals', []), first_name, tone)
    
    # Build the letter
    today = date.today().strftime('%B %d, %Y')
    
    body = f"""{today}

{greeting},

I hope this letter finds you well. I am writing to share {first_name}'s progress for the {period} reporting period.

{_get_opening_paragraph(first_name, tone, student)}

--- IEP GOAL PROGRESS ---

{goals_section}

--- GENERAL OBSERVATIONS ---

{_get_general_observations(first_name, student, tone)}

--- LOOKING AHEAD ---

{_get_looking_ahead(first_name, student, tone)}

Please don't hesitate to reach out if you have any questions or would like to discuss {first_name}'s progress further. I am always happy to schedule a meeting or phone call.

{tone_config['closing']},
{teacher_name or '[Teacher Name]'}
{student.get('classroom', '')}
{school_name or '[School Name]'}"""

    return {
        'type': 'progress_letter',
        'subject': f"{first_name}'s Progress Update - {period}",
        'body': body,
        'student_id': student.get('id'),
        'student_name': f"{first_name} {student.get('last_name', '')}".strip(),
        'period': period,
        'tone': tone,
        'generated_at': datetime.now().isoformat(),
        'metadata': {
            'goals_reported': len(student.get('iep_goals', [])),
            'tone_used': tone,
            'period': period
        }
    }


def _format_goals_progress(goals: list, student_name: str, tone: str) -> str:
    """Format IEP goals into readable progress summaries."""
    if not goals:
        return f"{student_name} continues to work on individualized goals. Detailed progress data is available upon request."
    
    sections = []
    for i, goal in enumerate(goals, 1):
        area = goal.get('area', 'Goal Area')
        goal_text = goal.get('goal', 'No goal text available')
        baseline = goal.get('baseline', 'N/A')
        current = goal.get('current', 'N/A')
        target = goal.get('target', 'N/A')
        status = goal.get('status', 'in progress')
        
        # Determine progress description
        progress_desc = _describe_progress(status, tone, student_name)
        
        section = f"""Goal {i}: {area}
  Objective: {goal_text}
  Baseline: {baseline} → Current: {current} (Target: {target})
  Status: {status.title()}
  {progress_desc}"""
        sections.append(section)
    
    return '\n\n'.join(sections)


def _describe_progress(status: str, tone: str, name: str) -> str:
    """Generate a human-readable progress description based on status."""
    descriptions = {
        'mastered': {
            'positive': f'🌟 {name} has mastered this goal! This is a wonderful achievement.',
            'professional': f'{name} has achieved mastery on this objective.',
            'warm': f'So proud of {name} — this goal is complete!',
            'concerned': f'{name} has met this goal.'
        },
        'on track': {
            'positive': f'{name} is making excellent progress toward this goal.',
            'professional': f'Progress is on track for the projected timeline.',
            'warm': f'{name} is doing great work on this!',
            'concerned': f'This goal area shows appropriate progress.'
        },
        'progressing': {
            'positive': f'{name} is showing growth in this area.',
            'professional': f'Data indicates measurable progress.',
            'warm': f'{name} is working hard and it shows!',
            'concerned': f'We are seeing some progress in this area.'
        },
        'limited progress': {
            'positive': f'We are continuing to support {name} with targeted strategies.',
            'professional': f'Progress has been limited; instructional adjustments are being implemented.',
            'warm': f"We're trying some new approaches to support {name} here.",
            'concerned': f'This is an area where {name} needs additional support. I would like to discuss strategies.'
        },
        'regression': {
            'positive': f'We have noticed some challenges and are adjusting our approach.',
            'professional': f'Data shows regression; the team is reviewing interventions.',
            'warm': f"We've noticed {name} needs extra help here — let's talk about how we can work together.",
            'concerned': f'I have concerns about this area and would like to discuss it with you.'
        }
    }
    
    status_lower = status.lower()
    tone_descriptions = descriptions.get(status_lower, descriptions.get('progressing', {}))
    return tone_descriptions.get(tone, f'{name} continues to work on this goal.')


def _get_opening_paragraph(name: str, tone: str, student: dict) -> str:
    """Generate an appropriate opening paragraph based on tone."""
    category = student.get('disability_category', '').lower()
    
    if tone == 'positive':
        return f"I am pleased to share the progress {name} has been making in our classroom. {name} has been working hard, and I want to highlight both achievements and ongoing areas of growth."
    elif tone == 'warm':
        return f"{name} has been doing wonderful things in class! I wanted to take a moment to share some updates with you about how things are going."
    elif tone == 'concerned':
        return f"I want to share an update on {name}'s progress. While there are areas of growth, there are also some areas I'd like to discuss with you so we can work together to support {name}."
    else:  # professional
        return f"This letter provides a summary of {name}'s progress on Individual Education Program (IEP) goals for the current reporting period."


def _get_general_observations(name: str, student: dict, tone: str) -> str:
    """Generate general observations placeholder."""
    return f"[Add 1-2 sentences about {name}'s social engagement, daily routines, and overall classroom participation.]"


def _get_looking_ahead(name: str, student: dict, tone: str) -> str:
    """Generate looking-ahead section."""
    if tone == 'concerned':
        return f"Moving forward, I would like to explore additional strategies to support {name}. It may be helpful for us to meet to discuss ways we can work together both at school and at home."
    elif tone == 'positive':
        return f"I am excited to continue building on {name}'s progress. In the coming weeks, we will focus on generalizing skills and increasing independence."
    else:
        return f"In the next reporting period, we will continue working on {name}'s IEP goals with a focus on skill generalization and increased independence."


# ─────────────────────────────────────────────────────────────────────
# DAILY BACKPACK LOG
# ─────────────────────────────────────────────────────────────────────

def generate_daily_log(student: dict, log_date: str, activities: list,
                       behavior: str, notes: str = '',
                       needs_supplies: list = None,
                       mood: str = 'good') -> dict:
    """
    Generate a daily backpack communication log.
    
    Args:
        student: Student dict
        log_date: Date string (will be formatted)
        activities: List of activity strings or dicts
        behavior: Overall behavior description or rating
        notes: Additional notes for parents
        needs_supplies: List of supplies needed from home
        mood: 'good', 'mixed', 'rough' — quick overall rating
        
    Returns:
        dict with formatted daily log
    """
    first_name = student.get('first_name', 'Your child')
    parent_name = student.get('parent_name', 'Family')
    
    # Format date nicely
    try:
        if isinstance(log_date, str):
            parsed_date = datetime.strptime(log_date, '%Y-%m-%d')
            formatted_date = parsed_date.strftime('%A, %B %d, %Y')
        else:
            formatted_date = log_date.strftime('%A, %B %d, %Y')
    except (ValueError, AttributeError):
        formatted_date = str(log_date)
    
    # Mood emoji/indicator
    mood_indicators = {
        'good': '😊 Great Day!',
        'mixed': '😐 Mixed Day',
        'rough': '😟 Tough Day'
    }
    mood_display = mood_indicators.get(mood, '📝 Daily Update')
    
    # Format activities
    activities_text = _format_activities(activities)
    
    # Build the log
    body = f"""╔══════════════════════════════════════════╗
║        DAILY COMMUNICATION LOG          ║
╚══════════════════════════════════════════╝

Student: {first_name}
Date: {formatted_date}
Overall: {mood_display}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TODAY WE WORKED ON:
{activities_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEHAVIOR/MOOD:
{behavior}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    if notes:
        body += f"""

NOTES:
{notes}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    if needs_supplies:
        supplies_list = '\n'.join(f'  □ {item}' for item in needs_supplies)
        body += f"""

📋 WE NEED FROM HOME:
{supplies_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    body += f"""

Please sign and return: _________________________

Questions? Notes for teacher: ___________________
________________________________________________

"""

    return {
        'type': 'daily_log',
        'subject': f"Daily Log - {first_name} - {formatted_date}",
        'body': body,
        'student_id': student.get('id'),
        'student_name': f"{first_name} {student.get('last_name', '')}".strip(),
        'date': log_date,
        'mood': mood,
        'generated_at': datetime.now().isoformat(),
        'metadata': {
            'activities_count': len(activities),
            'mood': mood,
            'supplies_needed': needs_supplies or []
        }
    }


def _format_activities(activities: list) -> str:
    """Format activities list for daily log."""
    if not activities:
        return "  • Regular classroom activities"
    
    lines = []
    for activity in activities:
        if isinstance(activity, dict):
            name = activity.get('name', 'Activity')
            detail = activity.get('detail', '')
            goal_area = activity.get('goal_area', '')
            line = f"  • {name}"
            if detail:
                line += f" — {detail}"
            if goal_area:
                line += f" (IEP: {goal_area})"
        else:
            line = f"  • {activity}"
        lines.append(line)
    
    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────
# BEHAVIOR UPDATE
# ─────────────────────────────────────────────────────────────────────

def generate_behavior_update(student: dict, incident: dict,
                             actions_taken: list,
                             tone: str = 'concerned',
                             teacher_name: str = '') -> dict:
    """
    Generate a behavior-specific communication.
    
    Args:
        student: Student dict
        incident: Dict with keys:
            - date, time, description, antecedent, behavior, consequence
            - severity: 'minor', 'moderate', 'major'
            - location, duration
        actions_taken: List of strings describing school response
        tone: Communication tone (usually 'concerned' or 'professional')
        teacher_name: Teacher's name
        
    Returns:
        dict with behavior update communication
    """
    first_name = student.get('first_name', 'your child')
    parent_name = student.get('parent_name', 'Family')
    tone_config = TONE_SETTINGS.get(tone, TONE_SETTINGS['concerned'])
    greeting = tone_config['greeting'].format(parent_name=parent_name)
    
    severity = incident.get('severity', 'moderate')
    incident_date = incident.get('date', date.today().strftime('%B %d, %Y'))
    
    # Actions taken formatted
    actions_text = '\n'.join(f"  • {action}" for action in actions_taken) if actions_taken else "  • Continued monitoring and support"
    
    # Severity-appropriate language
    severity_openers = {
        'minor': f"I wanted to let you know about something that happened today with {first_name}. This is not a major concern, but I like to keep you informed.",
        'moderate': f"I am writing to let you know about a situation involving {first_name} today. I want to make sure we are on the same page so we can support {first_name} together.",
        'major': f"I need to inform you about a significant behavioral incident involving {first_name} today. I want to discuss this with you and work together on next steps."
    }
    
    opener = severity_openers.get(severity, severity_openers['moderate'])
    
    body = f"""{greeting},

{opener}

WHAT HAPPENED:
  Date/Time: {incident_date} {incident.get('time', '')}
  Location: {incident.get('location', 'Classroom')}
  
  {incident.get('description', '[Description of incident]')}

"""

    # Include ABC data if available
    if incident.get('antecedent') or incident.get('behavior') or incident.get('consequence'):
        body += f"""BEHAVIORAL DETAILS:
  What happened before (Antecedent): {incident.get('antecedent', 'N/A')}
  The behavior: {incident.get('behavior', 'N/A')}
  What happened after (Consequence): {incident.get('consequence', 'N/A')}

"""

    body += f"""WHAT WE DID AT SCHOOL:
{actions_text}

HOW YOU CAN HELP AT HOME:
  • Please talk with {first_name} using simple, positive language
  • Reinforce the same expectations we use at school
  • Let me know if you notice anything different at home

"""

    if severity == 'major':
        body += f"""NEXT STEPS:
  I would like to schedule a time to talk with you about this. Please let me know
  what works for your schedule — a phone call, meeting before/after school, or
  a formal conference.

"""

    body += f"""Please don't hesitate to reach out with questions. We are a team working together for {first_name}'s success.

{tone_config['closing']},
{teacher_name or '[Teacher Name]'}"""

    return {
        'type': 'behavior_update',
        'subject': f"Behavior Update - {first_name} - {incident_date}",
        'body': body,
        'student_id': student.get('id'),
        'student_name': f"{first_name} {student.get('last_name', '')}".strip(),
        'severity': severity,
        'generated_at': datetime.now().isoformat(),
        'metadata': {
            'severity': severity,
            'incident_date': incident_date,
            'actions_count': len(actions_taken)
        }
    }


# ─────────────────────────────────────────────────────────────────────
# CELEBRATION NOTE
# ─────────────────────────────────────────────────────────────────────

def generate_celebration(student: dict, achievement: dict,
                         teacher_name: str = '') -> dict:
    """
    Generate a positive achievement celebration note.
    
    Args:
        student: Student dict
        achievement: Dict with keys:
            - title: Short description of achievement
            - description: Detailed description
            - goal_area: Related IEP goal area (optional)
            - date: When it happened
            - first_time: bool — is this a first-time accomplishment?
        teacher_name: Teacher's name
        
    Returns:
        dict with celebration communication
    """
    first_name = student.get('first_name', 'your child')
    parent_name = student.get('parent_name', 'Family')
    
    title = achievement.get('title', 'Amazing Progress')
    description = achievement.get('description', '')
    goal_area = achievement.get('goal_area', '')
    is_first = achievement.get('first_time', False)
    
    # Build celebration note
    body = f"""🌟 ⭐ 🌟 CELEBRATION NOTE 🌟 ⭐ 🌟

Hi {parent_name}!

I am SO excited to share some wonderful news about {first_name}!

✨ {title.upper()} ✨

{description}

"""

    if is_first:
        body += f"""This is the FIRST TIME {first_name} has done this! What a milestone! 🎉

"""

    if goal_area:
        body += f"""This achievement is connected to {first_name}'s IEP goal in {goal_area}.
It shows real, meaningful progress!

"""

    body += f"""Please celebrate with {first_name} at home! A high-five, a hug, or
their favorite activity would be a wonderful way to reinforce this success.

We are so proud of {first_name}'s hard work! 🌟

{teacher_name or '[Teacher Name]'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 Save this note — it's a keepsake of {first_name}'s growth!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return {
        'type': 'celebration',
        'subject': f"🌟 Celebration! {first_name} - {title}",
        'body': body,
        'student_id': student.get('id'),
        'student_name': f"{first_name} {student.get('last_name', '')}".strip(),
        'generated_at': datetime.now().isoformat(),
        'metadata': {
            'achievement_title': title,
            'goal_area': goal_area,
            'first_time': is_first
        }
    }


# ─────────────────────────────────────────────────────────────────────
# CONFERENCE PREP
# ─────────────────────────────────────────────────────────────────────

def generate_conference_prep(student: dict, conference_type: str = 'progress',
                             additional_topics: list = None) -> dict:
    """
    Generate talking points for parent-teacher conference.
    
    Args:
        student: Student dict with full data (goals, behavior, progress)
        conference_type: 'progress', 'annual_review', 'concern', 'initial'
        additional_topics: Extra topics to discuss
        
    Returns:
        dict with conference prep document
    """
    first_name = student.get('first_name', 'Student')
    last_name = student.get('last_name', '')
    parent_name = student.get('parent_name', 'Parent/Guardian')
    
    goals = student.get('iep_goals', [])
    
    body = f"""╔══════════════════════════════════════════════════════╗
║          CONFERENCE PREPARATION NOTES               ║
║          (Teacher Copy — DO NOT SEND HOME)          ║
╚══════════════════════════════════════════════════════╝

Student: {first_name} {last_name}
Parent/Guardian: {parent_name}
Conference Type: {conference_type.replace('_', ' ').title()}
Date: _______________

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPENING (Start Positive):
  • Greet parent warmly
  • Share something positive about {first_name}
  • "[Specific positive observation]"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IEP GOAL PROGRESS:
"""

    if goals:
        for i, goal in enumerate(goals, 1):
            area = goal.get('area', 'Goal')
            current = goal.get('current', 'N/A')
            target = goal.get('target', 'N/A')
            status = goal.get('status', 'in progress')
            
            body += f"""
  Goal {i}: {area}
    Current Level: {current}
    Target: {target}
    Status: {status}
    Talking Points:
      • [What has worked]
      • [What we're trying next]
      • [How parent can support at home]
"""
    else:
        body += """
  [No IEP goals loaded — bring goal progress data to meeting]
"""

    body += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEHAVIOR & SOCIAL:
  • Overall behavior pattern: _______________
  • Social interactions: _______________
  • Self-regulation: _______________
  • Communication growth: _______________

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DAILY LIVING / SELF-CARE:
  • Eating/lunch routine: _______________
  • Toileting: _______________
  • Dressing/coat/backpack: _______________
  • Transitions: _______________

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRENGTHS TO HIGHLIGHT:
  • 
  • 
  • 

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONCERNS TO ADDRESS:
  • 
  • 

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    if additional_topics:
        body += "\nADDITIONAL TOPICS:\n"
        for topic in additional_topics:
            body += f"  • {topic}\n"
        body += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    body += f"""
QUESTIONS TO ASK PARENT:
  • How is {first_name} doing at home?
  • Are you seeing any of these skills at home?
  • What are your goals/hopes for {first_name} this year?
  • Is there anything happening at home I should know about?
  • Do you have concerns you'd like to discuss?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLOSING:
  • Summarize action items
  • Set next communication date
  • Thank parent for their partnership
  • "We're a team working together for {first_name}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NOTES FROM MEETING:
___________________________________________________
___________________________________________________
___________________________________________________
___________________________________________________
"""

    return {
        'type': 'conference_prep',
        'subject': f"Conference Prep - {first_name} {last_name}",
        'body': body,
        'student_id': student.get('id'),
        'student_name': f"{first_name} {last_name}".strip(),
        'conference_type': conference_type,
        'generated_at': datetime.now().isoformat(),
        'metadata': {
            'conference_type': conference_type,
            'goals_count': len(goals),
            'additional_topics': additional_topics or []
        }
    }


# ─────────────────────────────────────────────────────────────────────
# COMMUNICATION HISTORY TRACKING
# ─────────────────────────────────────────────────────────────────────

class CommunicationLog:
    """Track sent communications for documentation purposes."""
    
    def __init__(self):
        self._history = []
    
    def record(self, communication: dict, sent: bool = True):
        """Record a communication as sent or drafted."""
        entry = {
            'id': len(self._history) + 1,
            'type': communication.get('type'),
            'student_id': communication.get('student_id'),
            'student_name': communication.get('student_name'),
            'subject': communication.get('subject'),
            'sent': sent,
            'sent_at': datetime.now().isoformat() if sent else None,
            'generated_at': communication.get('generated_at'),
            'metadata': communication.get('metadata', {})
        }
        self._history.append(entry)
        return entry
    
    def get_history(self, student_id: str = None, comm_type: str = None,
                    limit: int = 50) -> list:
        """Retrieve communication history with optional filters."""
        results = self._history
        
        if student_id:
            results = [h for h in results if h['student_id'] == student_id]
        if comm_type:
            results = [h for h in results if h['type'] == comm_type]
        
        return sorted(results, key=lambda x: x.get('generated_at', ''), reverse=True)[:limit]
    
    def get_last_communication(self, student_id: str) -> Optional[dict]:
        """Get the most recent communication for a student."""
        history = self.get_history(student_id=student_id, limit=1)
        return history[0] if history else None


# Module-level communication log instance
comm_log = CommunicationLog()
