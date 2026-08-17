"""
Aide Training Packet Generator for SPARK
Auto-generates training materials from student profile data for new aides/floaters.
"""

import json
import os
from datetime import datetime


def generate_aide_packet(students, config):
    """Generate a comprehensive aide training packet.
    
    Args:
        students: List of student dicts
        config: App config dict
    
    Returns:
        dict with training packet sections
    """
    packet = {
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "classroom_overview": {
            "teacher": config.get("teacher_name", ""),
            "school": config.get("school_name", ""),
            "class_type": "MSD (Moderate/Severe Disabilities)",
            "class_size": len(students),
            "schedule": f"{config.get('school_start_time', '8:00')} - {config.get('school_end_time', '2:35')}",
        },
        "general_expectations": [
            "Always maintain line of sight with assigned students",
            "Follow the posted visual schedule — consistency is critical",
            "Use the student\'s communication system (not just verbal directions)",
            "Reinforcement FIRST — redirect behavior by offering what TO do, not what NOT to do",
            "Document data during activities when possible (data sheets in binder)",
            "If unsure, ASK the lead teacher before making a judgment call",
            "Never leave a student unattended, even briefly",
            "Confidentiality is absolute — no photos, no sharing names outside the team",
        ],
        "communication_primer": {
            "AAC": "Augmentative/Alternative Communication device (tablet). Model by pressing buttons yourself. Give 10+ seconds wait time. Keep device within reach.",
            "PECS": "Picture Exchange Communication System. Student hands you a picture card to request. Accept card, say the word aloud, honor the request immediately.",
            "Sign Language": "Student uses manual signs. Common signs are posted in the classroom. Ask lead teacher for the student\'s core signs.",
            "Verbal (limited)": "Student uses some words/phrases. Use short, clear sentences. Pair with visuals. Give extra processing time.",
            "Gestures/Body Language": "Student communicates through pointing, reaching, leading, facial expressions. Watch carefully and narrate what you think they want: \'I see you pointing at the water. You want water?\'",
        },
        "student_profiles": [],
    }
    
    # Build per-student training profiles
    for student in students:
        profile = {
            "name": student.get("name", "Student"),
            "communication": {
                "mode": student.get("communication_mode", "Unknown"),
                "how_to_use": _get_comm_how_to(student),
                "how_they_say_yes": student.get("yes_signal", "Nod or smile"),
                "how_they_say_no": student.get("no_signal", "Push away or turn head"),
            },
            "behavior": {
                "triggers": student.get("behavior_triggers", "Ask lead teacher"),
                "warning_signs": student.get("warning_signs", "Watch for changes in body tension, vocalizations, or withdrawal"),
                "deescalation": student.get("deescalation_strategies", "Give space, reduce demands, offer a break"),
                "never_do": student.get("behavior_never_do", "Do not raise voice, physically block, or remove reinforcers as punishment"),
            },
            "reinforcers": {
                "items": student.get("reinforcers", []) if isinstance(student.get("reinforcers"), list) else [student.get("reinforcers", "Ask lead teacher")],
                "how_to_deliver": student.get("reinforcer_delivery", "Immediately after desired behavior. Pair with specific praise: \'Great job [action]!\'"),
                "schedule": student.get("reinforcement_schedule", "After each task completion initially; fade as student shows mastery"),
            },
            "physical_needs": {
                "positioning": student.get("positioning_needs", "Standard seating"),
                "mobility": student.get("mobility_notes", "Independent"),
                "toileting": student.get("toileting_needs", "Ask lead teacher for schedule"),
                "feeding": student.get("feeding_notes", "Independent or see mealtime chart"),
            },
            "sensory": {
                "needs": student.get("sensory_needs", "None noted"),
                "accommodations": student.get("sensory_accommodations", "See posted sensory diet"),
                "avoid": student.get("sensory_avoid", "Ask lead teacher"),
            },
            "daily_routine": student.get("daily_routine_notes", "Follow classroom visual schedule"),
        }
        
        packet["student_profiles"].append(profile)
    
    return packet


def _get_comm_how_to(student):
    """Generate specific how-to instructions for the student\'s communication."""
    mode = student.get("communication_mode", "").lower()
    
    if "aac" in mode:
        return "Their device is a [tablet/iPad]. Keep it charged and within reach. To model: press the buttons yourself to show them what to say. Core words are on the home screen. Give at least 10 seconds wait time after modeling."
    elif "pecs" in mode:
        return "Their PECS book/strip is attached to [location]. They will hand you a picture card. Take the card, say the word clearly, and give them what they requested. If they reach without a card, prompt them: \'Use your pictures.\'"
    elif "sign" in mode:
        return "Their most-used signs are posted at their work area. Key signs to know: MORE, DONE, HELP, BREAK, BATHROOM. Ask lead teacher to show you any student-specific signs."
    elif "verbal" in mode:
        return "They can speak but may need extra time to process and respond. Use short sentences (3-5 words). Wait 10 seconds before repeating. Do not finish their sentences."
    else:
        return "Ask the lead teacher to show you how this student communicates. Watch for any consistent gestures, sounds, or movements they use to express wants/needs."


def format_packet_for_print(packet):
    """Format the training packet as printable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("AIDE TRAINING PACKET")
    lines.append(f"Classroom: {packet['classroom_overview']['teacher']}")
    lines.append(f"Generated: {packet['generated_date']}")
    lines.append("=" * 60)
    lines.append("")
    
    lines.append("GENERAL EXPECTATIONS:")
    for exp in packet["general_expectations"]:
        lines.append(f"  ✓ {exp}")
    lines.append("")
    
    lines.append("-" * 60)
    lines.append("COMMUNICATION MODES IN THIS CLASSROOM")
    lines.append("-" * 60)
    for mode, desc in packet["communication_primer"].items():
        lines.append(f"\n  {mode}:")
        lines.append(f"    {desc}")
    lines.append("")
    
    lines.append("-" * 60)
    lines.append("INDIVIDUAL STUDENT PROFILES")
    lines.append("-" * 60)
    
    for p in packet["student_profiles"]:
        lines.append(f"\n{'='*40}")
        lines.append(f"★ {p['name']}")
        lines.append(f"{'='*40}")
        lines.append(f"  Communication: {p['communication']['mode']}")
        lines.append(f"  How to use: {p['communication']['how_to_use']}")
        lines.append(f"  \'Yes\' signal: {p['communication']['how_they_say_yes']}")
        lines.append(f"  \'No\' signal: {p['communication']['how_they_say_no']}")
        lines.append(f"\n  Behavior triggers: {p['behavior']['triggers']}")
        lines.append(f"  Warning signs: {p['behavior']['warning_signs']}")
        lines.append(f"  De-escalation: {p['behavior']['deescalation']}")
        lines.append(f"  NEVER: {p['behavior']['never_do']}")
        reinf_items = ', '.join(p['reinforcers']['items'])
        lines.append(f"\n  Reinforcers: {reinf_items}")
        lines.append(f"  How to deliver: {p['reinforcers']['how_to_deliver']}")
        lines.append(f"\n  Physical/positioning: {p['physical_needs']['positioning']}")
        lines.append(f"  Sensory needs: {p['sensory']['needs']}")
        lines.append(f"  Sensory avoid: {p['sensory']['avoid']}")
    
    return "\n".join(lines)
