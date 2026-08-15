"""
Student Manager Module
Handles CRUD operations for student profiles stored as local JSON.
Expanded for IEP compliance, behavioral, sensory, and life skills tracking.
"""

import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
STUDENTS_FILE = os.path.join(DATA_DIR, 'students.json')


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'knowledge_base'), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'lesson_plans'), exist_ok=True)
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'w') as f:
            json.dump([], f)


def get_all_students():
    """Get all student profiles."""
    ensure_data_dir()
    try:
        with open(STUDENTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def get_student(student_id):
    """Get a single student by ID."""
    students = get_all_students()
    for student in students:
        if student['id'] == student_id:
            return student
    return None


def add_student(student_data):
    """Add a new student profile."""
    ensure_data_dir()
    students = get_all_students()
    
    student = {
        'id': str(uuid.uuid4()),
        'name': student_data.get('name', ''),
        'age': student_data.get('age', ''),
        'grade': student_data.get('grade', ''),
        # IEP & Goals
        'iep_goals': student_data.get('iep_goals', []),
        'iep_annual_review_date': student_data.get('iep_annual_review_date', ''),
        'related_services': student_data.get('related_services', ''),
        'sdi_notes': student_data.get('sdi_notes', ''),
        # Needs
        'physical_needs': student_data.get('physical_needs', []),
        'cognitive_needs': student_data.get('cognitive_needs', ''),
        'behavioral_needs': student_data.get('behavioral_needs', ''),
        'sensory_needs': student_data.get('sensory_needs', ''),
        # Communication
        'communication_mode': student_data.get('communication_mode', ''),
        'communication_details': student_data.get('communication_details', ''),
        # Homeroom
        'homeroom_attends': student_data.get('homeroom_attends', False),
        'homeroom_duration': student_data.get('homeroom_duration', ''),
        'homeroom_aide_accompanies': student_data.get('homeroom_aide_accompanies', False),
        'homeroom_schedule': student_data.get('homeroom_schedule', ''),
        # Instructional
        'focus_areas': student_data.get('focus_areas', []),
        'reinforcers': student_data.get('reinforcers', ''),
        'prompting_level': student_data.get('prompting_level', ''),
        'life_skills_priorities': student_data.get('life_skills_priorities', []),
        # Notes (grows over time)
        'notes': student_data.get('notes', ''),
        'progress_notes': student_data.get('progress_notes', []),
        # Meta
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    students.append(student)
    _save_students(students)
    return student


def update_student(student_id, student_data):
    """Update an existing student profile."""
    students = get_all_students()
    
    for i, student in enumerate(students):
        if student['id'] == student_id:
            # Update all fields
            for key in student_data:
                if key not in ('id', 'created_at'):
                    student[key] = student_data[key]
            student['updated_at'] = datetime.now().isoformat()
            students[i] = student
            _save_students(students)
            return student
    
    return None


def add_progress_note(student_id, note):
    """Add a progress note to a student's dossier."""
    students = get_all_students()
    for i, student in enumerate(students):
        if student['id'] == student_id:
            if 'progress_notes' not in student:
                student['progress_notes'] = []
            student['progress_notes'].append({
                'date': datetime.now().isoformat(),
                'note': note
            })
            student['updated_at'] = datetime.now().isoformat()
            students[i] = student
            _save_students(students)
            return True
    return False


def delete_student(student_id):
    """Delete a student profile."""
    students = get_all_students()
    students = [s for s in students if s['id'] != student_id]
    _save_students(students)
    return True


def _save_students(students):
    """Save students list to JSON file."""
    ensure_data_dir()
    with open(STUDENTS_FILE, 'w') as f:
        json.dump(students, f, indent=2)
