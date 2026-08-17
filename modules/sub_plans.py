"""
Sub Plans Generator for SPARK
Generates comprehensive substitute teacher plans from existing student data.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def generate_sub_plan(students, config, schedule=None):
    """Generate a comprehensive substitute teacher plan.
    
    Args:
        students: List of student dicts from student_manager
        config: App config dict
        schedule: Optional schedule dict from schedule_engine
    
    Returns:
        dict with sub plan sections
    """
    plan = {
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "classroom_info": {
            "teacher_name": config.get("teacher_name", ""),
            "school_name": config.get("school_name", ""),
            "class_size": len(students),
            "num_aides": config.get("num_aides", 2),
            "has_floater": config.get("has_floater", True),
            "start_time": config.get("school_start_time", "8:00"),
            "end_time": config.get("school_end_time", "2:35"),
        },
        "emergency_info": {
            "office_phone": config.get("office_phone", "[See office]"),
            "nurse_location": config.get("nurse_location", "[See office]"),
            "admin_contact": config.get("admin_contact", "[See office]"),
        },
        "general_notes": [
            "This is a self-contained MSD classroom. Students have significant support needs.",
            "Follow the visual schedule posted on the wall.",
            "ALL transitions require verbal AND visual cues (countdown timer + 'first/then' board).",
            "If a student becomes escalated, use the de-escalation strategies listed in their section.",
            "Do NOT remove reinforcers as punishment.",
            "Aides know the students well — lean on them for guidance.",
            "If unsure about anything, ask an aide before acting.",
        ],
        "student_summaries": [],
        "daily_schedule_overview": [],
        "if_then_guide": [],
    }
    
    # Build per-student summaries
    for student in students:
        summary = {
            "name": student.get("name", "Student"),
            "communication_mode": student.get("communication_mode", "Unknown"),
            "communication_notes": _get_comm_instructions(student),
            "key_needs": [],
            "behavior_strategies": [],
            "reinforcers": student.get("reinforcers", []) if isinstance(student.get("reinforcers"), list) else [student.get("reinforcers", "")],
            "medical_alerts": student.get("medical_alerts", "None noted"),
            "sensory_needs": student.get("sensory_needs", "None noted"),
            "emergency_contacts": student.get("emergency_contacts", []),
        }
        
        # Key needs
        if student.get("physical_needs"):
            summary["key_needs"].append(f"Physical: {student['physical_needs']}")
        if student.get("behavioral_needs"):
            summary["key_needs"].append(f"Behavioral: {student['behavioral_needs']}")
        if student.get("sensory_needs"):
            summary["key_needs"].append(f"Sensory: {student['sensory_needs']}")
        
        # Behavior strategies
        if student.get("deescalation_strategies"):
            if isinstance(student["deescalation_strategies"], list):
                summary["behavior_strategies"] = student["deescalation_strategies"]
            else:
                summary["behavior_strategies"] = [student["deescalation_strategies"]]
        
        plan["student_summaries"].append(summary)
    
    # Build if/then quick reference
    plan["if_then_guide"] = [
        {"if": "A student refuses to transition", "then": "Use the visual timer (3-2-1), show the 'first/then' board, offer a choice of walking or being walked with an aide"},
        {"if": "A student is crying/screaming", "then": "Check if they are in pain, hungry, or overwhelmed. Offer a break in the calm corner. Do NOT demand eye contact or verbal responses."},
        {"if": "A student elopes (tries to leave the room)", "then": "One adult follows at a safe distance. Do NOT chase. Radio the office if they leave the hallway. Other adults stay with remaining students."},
        {"if": "A student is aggressive (hitting/biting)", "then": "Ensure other students are safe first. Give space. Use calm, low voice. Do NOT physically restrain unless trained and imminent danger. Call office if needed."},
        {"if": "A student has a seizure", "then": "Note the time. Clear the area. Turn on side if possible. Do NOT put anything in mouth. Call office and 911 if >5 minutes."},
        {"if": "A student toileting accident", "then": "Handle discreetly. Extra clothes in their cubby. Aide can assist. Log in daily notes."},
        {"if": "Fire drill / emergency", "then": "Follow posted evacuation route. Bring the class binder (has medical info). Count heads. Some students may need physical guidance or headphones for noise."},
    ]
    
    return plan


def _get_comm_instructions(student):
    """Generate communication instructions for sub based on student's mode."""
    mode = student.get("communication_mode", "").lower()
    
    if "aac" in mode or "device" in mode:
        return "Uses an AAC device (tablet/app). It should be with them at all times. Model language by pressing buttons yourself. Give extra wait time (10+ seconds) for responses."
    elif "pecs" in mode or "picture" in mode:
        return "Uses PECS (Picture Exchange Communication System). Picture cards are in their binder/strip. They hand you a picture to make requests. Accept the picture, say the word, and honor the request."
    elif "sign" in mode:
        return "Uses sign language. Common signs are posted near their area. Aide can interpret if needed."
    elif "verbal" in mode and "limited" in mode:
        return "Has limited verbal speech. May use 1-2 word phrases. Give extra processing time. Pair verbal with visual cues."
    elif "verbal" in mode:
        return "Verbal communicator. May need extra processing time and simplified language."
    elif "gesture" in mode:
        return "Communicates primarily through gestures and body language. Watch for pointing, reaching, leading you by the hand."
    else:
        return "Check with an aide about this student's communication system."


def format_sub_plan_for_print(plan):
    """Format the sub plan as a printable text document."""
    lines = []
    lines.append("=" * 60)
    lines.append("SUBSTITUTE TEACHER PLAN")
    lines.append(f"Classroom: {plan['classroom_info']['teacher_name']}")
    lines.append(f"School: {plan['classroom_info']['school_name']}")
    lines.append(f"Date generated: {plan['generated_date']}")
    lines.append("=" * 60)
    lines.append("")
    
    lines.append("IMPORTANT NOTES:")
    for note in plan["general_notes"]:
        lines.append(f"  • {note}")
    lines.append("")
    
    lines.append("-" * 60)
    lines.append("STUDENT QUICK REFERENCE")
    lines.append("-" * 60)
    
    for s in plan["student_summaries"]:
        lines.append(f"\n★ {s['name']}")
        lines.append(f"  Communication: {s['communication_mode']}")
        lines.append(f"  → {s['communication_notes']}")
        if s["key_needs"]:
            needs_str = '; '.join(s['key_needs'])
            lines.append(f"  Needs: {needs_str}")
        if s["reinforcers"]:
            reinf_str = ', '.join(s['reinforcers'])
            lines.append(f"  Reinforcers: {reinf_str}")
        if s["behavior_strategies"]:
            strat_str = '; '.join(s['behavior_strategies'])
            lines.append(f"  De-escalation: {strat_str}")
        if s["medical_alerts"] and s["medical_alerts"] != "None noted":
            lines.append(f"  ⚠️ MEDICAL: {s['medical_alerts']}")
    
    lines.append("")
    lines.append("-" * 60)
    lines.append("IF/THEN QUICK GUIDE")
    lines.append("-" * 60)
    
    for item in plan["if_then_guide"]:
        lines.append(f"\n  IF: {item['if']}")
        lines.append(f"  THEN: {item['then']}")
    
    return "\n".join(lines)
