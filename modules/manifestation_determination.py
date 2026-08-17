"""
SPARK - Manifestation Determination Module
============================================
Implements the manifestation determination review (MDR) process
per Kentucky HB 538 and IDEA § 300.530.

A manifestation determination must occur within 10 school days of any
decision to change the placement of a student with a disability for
disciplinary reasons. The team determines:
1. Was the conduct caused by, or directly/substantially related to, 
   the student's disability?
2. Was the conduct a direct result of the LEA's failure to implement the IEP?

If either answer is YES → the behavior IS a manifestation of the disability
and the student cannot be subjected to the proposed disciplinary action
(with limited exceptions for drugs, weapons, serious bodily injury).

Reference:
- Kentucky HB 538 (2024) - Discipline of students with disabilities
- IDEA 2004 § 300.530 - Authority of school personnel
- 707 KAR 1:340 - Discipline procedures (Kentucky)
"""

from datetime import datetime, date
from typing import Optional, Dict, List, Any


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECKLIST STRUCTURE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MDR_CHECKLIST = {
    "pre_meeting": {
        "title": "Pre-Meeting Preparation",
        "description": "Gather before the MDR team convenes (within 10 school days of discipline decision)",
        "items": [
            {
                "id": "pre_1",
                "text": "Discipline incident documented with date, time, and description",
                "required": True
            },
            {
                "id": "pre_2",
                "text": "Copy of student\'s current IEP available for review",
                "required": True
            },
            {
                "id": "pre_3",
                "text": "Relevant behavior data and progress monitoring records pulled",
                "required": True
            },
            {
                "id": "pre_4",
                "text": "FBA/BIP reviewed (if one exists)",
                "required": True
            },
            {
                "id": "pre_5",
                "text": "Parent/guardian notified of MDR meeting and invited to participate",
                "required": True
            },
            {
                "id": "pre_6",
                "text": "Teacher observations and anecdotal notes gathered",
                "required": False
            },
            {
                "id": "pre_7",
                "text": "Medical/health information relevant to behavior reviewed",
                "required": False
            },
        ]
    },
    "team_composition": {
        "title": "MDR Team Members Present",
        "description": "The team must include the LEA, parent, and relevant IEP team members",
        "items": [
            {
                "id": "team_1",
                "text": "LEA representative (or designee) present",
                "required": True
            },
            {
                "id": "team_2",
                "text": "Parent/guardian present (or documented attempts to include)",
                "required": True
            },
            {
                "id": "team_3",
                "text": "Special education teacher present",
                "required": True
            },
            {
                "id": "team_4",
                "text": "General education teacher present (if applicable)",
                "required": False
            },
            {
                "id": "team_5",
                "text": "School psychologist or behavior specialist present (if applicable)",
                "required": False
            },
        ]
    },
    "determination_questions": {
        "title": "Manifestation Determination Questions",
        "description": "The two critical questions the team must answer",
        "items": [
            {
                "id": "det_1",
                "text": "Was the conduct in question CAUSED BY, or did it have a DIRECT AND SUBSTANTIAL RELATIONSHIP to, the student\'s disability?",
                "required": True,
                "type": "yes_no",
                "guidance": "Consider: Does the student\'s disability impair their ability to understand the impact of their behavior? Does the disability impair their ability to control their behavior?"
            },
            {
                "id": "det_2",
                "text": "Was the conduct in question the DIRECT RESULT of the LEA\'s failure to implement the IEP?",
                "required": True,
                "type": "yes_no",
                "guidance": "Consider: Were all IEP services being provided? Were accommodations and BIP strategies being implemented? Were SDI requirements being followed?"
            },
        ]
    },
    "outcome": {
        "title": "Determination Outcome",
        "description": "Based on the answers to the determination questions",
        "items": [
            {
                "id": "out_1",
                "text": "If YES to either question: Behavior IS a manifestation. Student returns to placement (unless parent and LEA agree to change). Conduct FBA and implement/revise BIP.",
                "type": "outcome_yes"
            },
            {
                "id": "out_2",
                "text": "If NO to both questions: Behavior is NOT a manifestation. School may apply disciplinary procedures as for non-disabled students, but FAPE must continue.",
                "type": "outcome_no"
            },
        ]
    },
    "exceptions_45_day": {
        "title": "Special Circumstances (45-Day Removal)",
        "description": "School may remove to interim alternative setting for up to 45 school days regardless of manifestation for:",
        "items": [
            {
                "id": "exc_1",
                "text": "Student carried/possessed a weapon at school or school function",
                "type": "exception"
            },
            {
                "id": "exc_2",
                "text": "Student knowingly possessed/used illegal drugs or sold/solicited controlled substance",
                "type": "exception"
            },
            {
                "id": "exc_3",
                "text": "Student inflicted serious bodily injury upon another person while at school or school function",
                "type": "exception"
            },
        ]
    },
    "post_determination": {
        "title": "Post-Determination Actions",
        "description": "Required follow-up regardless of outcome",
        "items": [
            {
                "id": "post_1",
                "text": "Written determination documented and filed",
                "required": True
            },
            {
                "id": "post_2",
                "text": "Parents provided copy of procedural safeguards",
                "required": True
            },
            {
                "id": "post_3",
                "text": "If manifestation: FBA conducted (or reviewed if existing)",
                "required": False,
                "condition": "manifestation_yes"
            },
            {
                "id": "post_4",
                "text": "If manifestation: BIP created or revised",
                "required": False,
                "condition": "manifestation_yes"
            },
            {
                "id": "post_5",
                "text": "If NOT manifestation: FAPE services continue during removal",
                "required": False,
                "condition": "manifestation_no"
            },
            {
                "id": "post_6",
                "text": "IEP team meeting scheduled to review/revise IEP if needed",
                "required": False
            },
        ]
    }
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HB 538 KEY PROVISIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HB_538_SUMMARY = {
    "bill": "Kentucky HB 538 (2024)",
    "effective_date": "2024-07-01",
    "key_provisions": [
        "Codifies federal IDEA discipline protections into Kentucky state law",
        "Requires school districts to conduct MDR within 10 school days",
        "Mandates that students with disabilities receive FAPE even during disciplinary removals",
        "Establishes clear criteria for 45-school-day interim alternative placements",
        "Requires written parental notification of procedural safeguards",
        "Aligns Kentucky discipline procedures with 707 KAR 1:340",
    ],
    "teacher_implications": [
        "Document all behavior incidents thoroughly with date/time/description",
        "Maintain up-to-date BIP implementation fidelity records",
        "Ensure IEP services are being provided as written (failure = automatic manifestation)",
        "Collect ongoing behavior data to support or refute disability relationship",
        "Participate in MDR meetings when requested",
    ]
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUBLIC API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_checklist():
    """Return the full MDR checklist structure."""
    return MDR_CHECKLIST


def get_hb538_summary():
    """Return HB 538 summary information."""
    return HB_538_SUMMARY


def get_checklist_section(section_key):
    """Get a specific section of the checklist."""
    return MDR_CHECKLIST.get(section_key)


def evaluate_determination(det_1_answer: bool, det_2_answer: bool) -> Dict[str, Any]:
    """
    Evaluate the manifestation determination based on the two key questions.
    
    Args:
        det_1_answer: True if conduct was caused by/related to disability
        det_2_answer: True if conduct resulted from failure to implement IEP
        
    Returns:
        Dict with determination result and required actions
    """
    is_manifestation = det_1_answer or det_2_answer
    
    result = {
        "is_manifestation": is_manifestation,
        "determination_date": datetime.now().isoformat(),
        "question_1_answer": det_1_answer,
        "question_2_answer": det_2_answer,
    }
    
    if is_manifestation:
        result["outcome"] = "MANIFESTATION - Behavior IS related to disability"
        result["required_actions"] = [
            "Return student to prior placement (unless parent/LEA agree otherwise)",
            "Conduct Functional Behavior Assessment (or review existing)",
            "Create or revise Behavior Intervention Plan",
            "Review and revise IEP as needed",
            "Document determination in writing",
            "Provide parents copy of procedural safeguards"
        ]
        if det_2_answer:
            result["required_actions"].append(
                "CRITICAL: Address IEP implementation failure immediately"
            )
    else:
        result["outcome"] = "NOT A MANIFESTATION - Standard discipline may apply"
        result["required_actions"] = [
            "School may apply same disciplinary procedures as non-disabled peers",
            "FAPE must continue during any period of removal",
            "Document determination in writing",
            "Provide parents copy of procedural safeguards",
            "Consider whether IEP/BIP revision is still appropriate"
        ]
    
    return result


def get_timeline_info() -> Dict[str, str]:
    """Return key timeline requirements for MDR process."""
    return {
        "trigger": "Any decision to change placement for disciplinary reasons",
        "mdr_deadline": "Within 10 SCHOOL DAYS of the discipline decision",
        "parent_notification": "Same day as discipline decision (or next school day)",
        "fape_continuation": "Must begin immediately upon removal exceeding 10 cumulative days",
        "appeal_window": "Parent may request due process hearing if they disagree with determination",
        "45_day_limit": "Maximum for interim alternative setting (special circumstances only)"
    }
