"""
Medical/Safety Sheets for SPARK
Generates printable per-student medical and safety information sheets.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
MEDICAL_DIR = os.path.join(DATA_DIR, 'medical')


def ensure_medical_dir():
    """Ensure the medical data directory exists."""
    os.makedirs(MEDICAL_DIR, exist_ok=True)


def get_medical_data(student_id):
    """Get medical/safety data for a student."""
    ensure_medical_dir()
    filepath = os.path.join(MEDICAL_DIR, f"{student_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return get_blank_medical_record()


def save_medical_data(student_id, data):
    """Save medical/safety data for a student."""
    ensure_medical_dir()
    filepath = os.path.join(MEDICAL_DIR, f"{student_id}.json")
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def get_blank_medical_record():
    """Return a blank medical record template."""
    return {
        "allergies": "",
        "medications": [],
        "seizure_protocol": {
            "has_seizures": False,
            "type": "",
            "protocol": "",
            "rescue_med": "",
            "rescue_med_location": "",
        },
        "elopement_risk": {
            "is_risk": False,
            "protocol": "",
            "triggers": "",
        },
        "emergency_contacts": [
            {"name": "", "relationship": "", "phone": "", "is_primary": True},
            {"name": "", "relationship": "", "phone": "", "is_primary": False},
        ],
        "hospital_preference": "",
        "doctor_name": "",
        "doctor_phone": "",
        "dietary_restrictions": "",
        "sensory_triggers": "",
        "physical_limitations": "",
        "toileting_needs": "",
        "additional_notes": "",
        "last_updated": "",
    }


def generate_safety_sheet(student, medical_data):
    """Generate a formatted safety sheet for printing.
    
    Args:
        student: Student dict from student_manager
        medical_data: Medical data dict
    
    Returns:
        dict with formatted sections for the template
    """
    sheet = {
        "student_name": student.get("name", "Unknown"),
        "classroom": student.get("classroom_type", "MSD"),
        "communication_mode": student.get("communication_mode", "Unknown"),
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "sections": {}
    }
    
    # Allergies section
    sheet["sections"]["allergies"] = {
        "has_data": bool(medical_data.get("allergies")),
        "content": medical_data.get("allergies", "No known allergies"),
        "severity": "high" if medical_data.get("allergies") else "none"
    }
    
    # Medications
    meds = medical_data.get("medications", [])
    sheet["sections"]["medications"] = {
        "has_data": len(meds) > 0,
        "items": meds,
        "content": "No medications" if not meds else None
    }
    
    # Seizure protocol
    seizure = medical_data.get("seizure_protocol", {})
    sheet["sections"]["seizure"] = {
        "has_data": seizure.get("has_seizures", False),
        "type": seizure.get("type", ""),
        "protocol": seizure.get("protocol", ""),
        "rescue_med": seizure.get("rescue_med", ""),
        "rescue_med_location": seizure.get("rescue_med_location", ""),
    }
    
    # Elopement
    elopement = medical_data.get("elopement_risk", {})
    sheet["sections"]["elopement"] = {
        "is_risk": elopement.get("is_risk", False),
        "protocol": elopement.get("protocol", ""),
        "triggers": elopement.get("triggers", ""),
    }
    
    # Emergency contacts
    contacts = medical_data.get("emergency_contacts", [])
    sheet["sections"]["emergency_contacts"] = {
        "contacts": contacts
    }
    
    # Other medical
    sheet["sections"]["other"] = {
        "hospital": medical_data.get("hospital_preference", ""),
        "doctor": medical_data.get("doctor_name", ""),
        "doctor_phone": medical_data.get("doctor_phone", ""),
        "dietary": medical_data.get("dietary_restrictions", ""),
        "sensory_triggers": medical_data.get("sensory_triggers", ""),
        "physical": medical_data.get("physical_limitations", ""),
        "toileting": medical_data.get("toileting_needs", ""),
        "notes": medical_data.get("additional_notes", ""),
    }
    
    return sheet


def get_all_medical_alerts(students):
    """Get a summary of all students with active medical alerts.
    
    Returns list of dicts with student_name and alert_types.
    """
    alerts = []
    for student in students:
        student_id = student.get("id", "")
        medical = get_medical_data(student_id)
        
        student_alerts = []
        if medical.get("allergies"):
            student_alerts.append("Allergies")
        if medical.get("seizure_protocol", {}).get("has_seizures"):
            student_alerts.append("Seizure protocol")
        if medical.get("elopement_risk", {}).get("is_risk"):
            student_alerts.append("Elopement risk")
        if medical.get("medications"):
            student_alerts.append(f"{len(medical['medications'])} medication(s)")
        
        if student_alerts:
            alerts.append({
                "student_name": student.get("name", "Unknown"),
                "student_id": student_id,
                "alerts": student_alerts
            })
    
    return alerts
