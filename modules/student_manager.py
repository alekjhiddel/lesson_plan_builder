"""
Student Manager Module
Handles CRUD operations for student profiles.
Supports both legacy format (single students.json) and new year-aware format
(per-student directories with profile.json + current_goals.json + lifecycle.json).
"""

import json
import os
import uuid
import shutil
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
STUDENTS_FILE = os.path.join(DATA_DIR, 'students.json')
STUDENTS_DIR = os.path.join(DATA_DIR, 'students')
CURRENT_YEAR_FILE = os.path.join(DATA_DIR, 'current_year.json')


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'knowledge_base'), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'lesson_plans'), exist_ok=True)


def _is_year_aware():
    """Check if the app is running in year-aware (migrated) mode."""
    return os.path.exists(CURRENT_YEAR_FILE)


def _get_current_year():
    """Get current year string for tagging new data."""
    if os.path.exists(CURRENT_YEAR_FILE):
        with open(CURRENT_YEAR_FILE, 'r') as f:
            data = json.load(f)
        return data.get('year', '2026-27')
    return '2026-27'


# ============================================================
# PUBLIC API — Same interface as before, auto-detects format
# ============================================================

def get_all_students():
    """Get all student profiles. Works in both old and new format."""
    ensure_data_dir()
    
    if _is_year_aware():
        return _get_all_students_new()
    else:
        return _get_all_students_legacy()


def get_student(student_id):
    """Get a single student by ID. Works in both formats."""
    if _is_year_aware():
        return _get_student_new(student_id)
    else:
        return _get_student_legacy(student_id)


def add_student(student_data):
    """Add a new student profile. Uses new format if migrated."""
    ensure_data_dir()
    
    student_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    student = {
        'id': student_id,
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
        # Notes
        'notes': student_data.get('notes', ''),
        'progress_notes': student_data.get('progress_notes', []),
        # Meta
        'created_at': now,
        'updated_at': now
    }
    
    if _is_year_aware():
        _save_student_new(student)
    else:
        students = _get_all_students_legacy()
        students.append(student)
        _save_students_legacy(students)
    
    return student


def update_student(student_id, student_data):
    """Update an existing student profile."""
    if _is_year_aware():
        return _update_student_new(student_id, student_data)
    else:
        return _update_student_legacy(student_id, student_data)


def add_progress_note(student_id, note):
    """Add a progress note to a student's dossier."""
    student = get_student(student_id)
    if not student:
        return False
    
    if 'progress_notes' not in student:
        student['progress_notes'] = []
    student['progress_notes'].append({
        'date': datetime.now().isoformat(),
        'note': note
    })
    
    update_student(student_id, student)
    return True


def delete_student(student_id):
    """Delete a student profile."""
    if _is_year_aware():
        return _delete_student_new(student_id)
    else:
        return _delete_student_legacy(student_id)


# ============================================================
# LEGACY FORMAT — Single students.json file
# ============================================================

def _get_all_students_legacy():
    """Load all students from the flat students.json."""
    if not os.path.exists(STUDENTS_FILE):
        return []
    try:
        with open(STUDENTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _get_student_legacy(student_id):
    """Get single student from legacy format."""
    students = _get_all_students_legacy()
    for student in students:
        if student['id'] == student_id:
            return student
    return None


def _update_student_legacy(student_id, student_data):
    """Update student in legacy format."""
    students = _get_all_students_legacy()
    for i, student in enumerate(students):
        if student['id'] == student_id:
            for key in student_data:
                if key not in ('id', 'created_at'):
                    student[key] = student_data[key]
            student['updated_at'] = datetime.now().isoformat()
            students[i] = student
            _save_students_legacy(students)
            return student
    return None


def _delete_student_legacy(student_id):
    """Delete student from legacy format."""
    students = _get_all_students_legacy()
    students = [s for s in students if s['id'] != student_id]
    _save_students_legacy(students)
    return True


def _save_students_legacy(students):
    """Save students list to the flat JSON file."""
    ensure_data_dir()
    with open(STUDENTS_FILE, 'w') as f:
        json.dump(students, f, indent=2)


# ============================================================
# NEW FORMAT — Per-student directories
# ============================================================

def _get_all_students_new():
    """Load all students from directory structure, merged into flat dicts."""
    if not os.path.exists(STUDENTS_DIR):
        return []
    
    students = []
    for entry in os.listdir(STUDENTS_DIR):
        student_dir = os.path.join(STUDENTS_DIR, entry)
        if os.path.isdir(student_dir):
            profile_path = os.path.join(student_dir, 'profile.json')
            if os.path.exists(profile_path):
                student = _load_merged_student(student_dir)
                if student:
                    students.append(student)
    
    # Sort by name for consistent ordering
    students.sort(key=lambda s: s.get('name', '').lower())
    return students


def _get_student_new(student_id):
    """Get single student from new directory format."""
    student_dir = os.path.join(STUDENTS_DIR, student_id)
    if os.path.isdir(student_dir):
        return _load_merged_student(student_dir)
    return None


def _load_merged_student(student_dir):
    """
    Load a student from directory structure and merge into a single dict.
    This provides backward compatibility — the rest of the app sees the same
    dict shape regardless of storage format.
    """
    profile_path = os.path.join(student_dir, 'profile.json')
    goals_path = os.path.join(student_dir, 'current_goals.json')
    lifecycle_path = os.path.join(student_dir, 'lifecycle.json')
    
    try:
        # Profile is required
        with open(profile_path, 'r') as f:
            student = json.load(f)
        
        # Goals are optional (might not exist yet for a brand new student)
        if os.path.exists(goals_path):
            with open(goals_path, 'r') as f:
                goals = json.load(f)
            # Merge goals into the student dict (skip the 'year' key)
            for key, value in goals.items():
                if key != 'year':
                    student[key] = value
        
        # Lifecycle is optional (adds status info)
        if os.path.exists(lifecycle_path):
            with open(lifecycle_path, 'r') as f:
                lifecycle = json.load(f)
            # Add lifecycle fields with a prefix to avoid collision
            student['_lifecycle_status'] = lifecycle.get('current_status', 'active')
            student['_lifecycle_grade'] = lifecycle.get('current_grade', '')
            student['_entry_year'] = lifecycle.get('entry_year', '')
            student['_expected_transition'] = lifecycle.get('expected_transition_year', '')
        
        return student
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return None


def _save_student_new(student):
    """Save a new student in directory format."""
    from modules.migration import PROFILE_FIELDS, GOALS_FIELDS
    
    student_id = student['id']
    student_dir = os.path.join(STUDENTS_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)
    
    year = _get_current_year()
    
    # Split into profile and goals
    profile = {}
    goals = {'year': year}
    
    for key, value in student.items():
        if key in PROFILE_FIELDS:
            profile[key] = value
        elif key in GOALS_FIELDS:
            goals[key] = value
    
    profile['id'] = student_id
    
    # Save profile
    with open(os.path.join(student_dir, 'profile.json'), 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Save goals
    with open(os.path.join(student_dir, 'current_goals.json'), 'w') as f:
        json.dump(goals, f, indent=2)
    
    # Create lifecycle if it doesn't exist
    lifecycle_path = os.path.join(student_dir, 'lifecycle.json')
    if not os.path.exists(lifecycle_path):
        from modules.year_lifecycle import create_default_lifecycle
        grade = student.get('grade', 'unknown')
        create_default_lifecycle(student_id, grade, year)


def _update_student_new(student_id, student_data):
    """Update a student in directory format."""
    from modules.migration import PROFILE_FIELDS, GOALS_FIELDS
    
    student_dir = os.path.join(STUDENTS_DIR, student_id)
    if not os.path.isdir(student_dir):
        return None
    
    profile_path = os.path.join(student_dir, 'profile.json')
    goals_path = os.path.join(student_dir, 'current_goals.json')
    
    # Load existing
    profile = {}
    goals = {}
    
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            profile = json.load(f)
    
    if os.path.exists(goals_path):
        with open(goals_path, 'r') as f:
            goals = json.load(f)
    
    # Update fields in the appropriate file
    for key, value in student_data.items():
        if key in ('id', 'created_at'):
            continue  # Never overwrite these
        if key.startswith('_lifecycle'):
            continue  # Don't write internal lifecycle fields back
        if key in PROFILE_FIELDS:
            profile[key] = value
        elif key in GOALS_FIELDS:
            goals[key] = value
        else:
            # Unknown field — put in profile as catch-all
            profile[key] = value
    
    profile['updated_at'] = datetime.now().isoformat()
    
    # Save both
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    
    with open(goals_path, 'w') as f:
        json.dump(goals, f, indent=2)
    
    # Return merged view
    return _load_merged_student(student_dir)


def _delete_student_new(student_id):
    """Delete a student directory."""
    student_dir = os.path.join(STUDENTS_DIR, student_id)
    if os.path.isdir(student_dir):
        shutil.rmtree(student_dir)
        return True
    return False
