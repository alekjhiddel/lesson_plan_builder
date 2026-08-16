"""
Partner Sync Module
Handles export/import of student data between partner teachers.
Exports operational info (not full IEP goals) that partners need for coverage,
scheduling, and safety. Partners are both bound by FERPA so names can be shared
between connected rooms.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PARTNER_STUDENTS_FILE = os.path.join(DATA_DIR, 'partner_students.json')


def export_for_partner(students, config):
    """
    Generate a shareable summary of classroom students for a partner teacher.
    Includes operational info they need for coverage/scheduling/safety.
    Does NOT include full IEP goals (that's confidential to the caseload teacher).
    
    Returns a formatted text block that can be copied/pasted or saved to a file.
    """
    export_data = {
        'export_version': 1,
        'exported_at': datetime.now().isoformat(),
        'teacher_name': config.get('teacher_name', 'Partner'),
        'program_type': config.get('program_type', 'msd'),
        'num_students': len(students),
        'students': []
    }
    
    for student in students:
        # Only export what a partner needs operationally
        partner_view = {
            'name': student.get('name', ''),
            'age': student.get('age', ''),
            'grade': student.get('grade', ''),
            'communication_mode': student.get('communication_mode', ''),
            'communication_details': student.get('communication_details', ''),
            'physical_needs': student.get('physical_needs', []),
            'behavioral_needs': student.get('behavioral_needs', ''),
            'sensory_needs': student.get('sensory_needs', ''),
            'reinforcers': student.get('reinforcers', ''),
            'medical_alerts': student.get('medical_alerts', []),
            'homeroom_attends': student.get('homeroom_attends', False),
            'homeroom_duration': student.get('homeroom_duration', ''),
            'homeroom_aide_accompanies': student.get('homeroom_aide_accompanies', False),
            'homeroom_schedule': student.get('homeroom_schedule', ''),
            # Basic info about what they're working on (not detailed IEP goals)
            'focus_areas': student.get('focus_areas', []),
            'notes': student.get('notes', '')
        }
        export_data['students'].append(partner_view)
    
    return json.dumps(export_data, indent=2)


def import_partner_students(import_text):
    """
    Import partner teacher's student data from their export.
    Tags all imported students as partner_student=True so they appear
    in scheduling/coverage but NOT in IEP/progress features.
    
    Returns dict with success status and count of students imported.
    """
    try:
        data = json.loads(import_text)
        
        if 'students' not in data:
            return {'success': False, 'error': 'Invalid format — no student data found. Make sure you pasted the full export.'}
        
        partner_name = data.get('teacher_name', 'Partner')
        
        # Load existing partner students
        existing = get_partner_students()
        
        # Remove any previous import from the same teacher
        existing = [s for s in existing if s.get('partner_teacher_name') != partner_name]
        
        # Add new partner students
        imported_count = 0
        for student_data in data['students']:
            student_data['is_partner_student'] = True
            student_data['partner_teacher_name'] = partner_name
            student_data['imported_at'] = datetime.now().isoformat()
            existing.append(student_data)
            imported_count += 1
        
        _save_partner_students(existing)
        
        return {
            'success': True,
            'count': imported_count,
            'partner_name': partner_name,
            'message': f'Imported {imported_count} students from {partner_name}!'
        }
    
    except json.JSONDecodeError:
        return {'success': False, 'error': 'Could not read the data. Make sure you pasted the complete export text (it starts with { and ends with }).'}
    except Exception as e:
        return {'success': False, 'error': f'Import failed: {str(e)[:200]}'}


def get_partner_students():
    """Get all imported partner students."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PARTNER_STUDENTS_FILE):
        return []
    try:
        with open(PARTNER_STUDENTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def delete_partner_students(partner_name=None):
    """Delete partner students (optionally filtered by partner teacher name)."""
    if partner_name:
        students = get_partner_students()
        students = [s for s in students if s.get('partner_teacher_name') != partner_name]
        _save_partner_students(students)
    else:
        _save_partner_students([])
    return True


def get_partner_classroom_summary():
    """
    Get a summary of the partner's classroom for display.
    Returns dict with partner name, student count, and key info.
    """
    students = get_partner_students()
    if not students:
        return None
    
    # Group by partner teacher
    partners = {}
    for s in students:
        name = s.get('partner_teacher_name', 'Partner')
        if name not in partners:
            partners[name] = []
        partners[name].append(s)
    
    summaries = []
    for partner_name, partner_students in partners.items():
        homeroom_count = sum(1 for s in partner_students if s.get('homeroom_attends'))
        aide_escort_count = sum(1 for s in partner_students if s.get('homeroom_aide_accompanies'))
        
        summaries.append({
            'partner_name': partner_name,
            'num_students': len(partner_students),
            'students': partner_students,
            'homeroom_count': homeroom_count,
            'aide_escort_count': aide_escort_count
        })
    
    return summaries


def _save_partner_students(students):
    """Save partner students to file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PARTNER_STUDENTS_FILE, 'w') as f:
        json.dump(students, f, indent=2)
