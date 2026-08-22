"""
Migration Module
Handles one-time migration from flat student storage to year-aware directory structure.
Safe to run multiple times — detects if already migrated and no-ops.
"""

import json
import os
import shutil
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
STUDENTS_FILE = os.path.join(DATA_DIR, 'students.json')
STUDENTS_DIR = os.path.join(DATA_DIR, 'students')
CURRENT_YEAR_FILE = os.path.join(DATA_DIR, 'current_year.json')
BACKUP_FILE = os.path.join(DATA_DIR, 'students_pre_migration_backup.json')

# Fields that belong in profile.json (persistent across years)
PROFILE_FIELDS = {
    'id', 'name', 'age', 'grade',
    'physical_needs', 'cognitive_needs', 'behavioral_needs', 'sensory_needs',
    'communication_mode', 'communication_details',
    'homeroom_attends', 'homeroom_duration', 'homeroom_aide_accompanies', 'homeroom_schedule',
    'reinforcers', 'prompting_level',
    'related_services', 'sdi_notes',
    'iep_annual_review_date',
    'notes',
    'created_at', 'updated_at'
}

# Fields that belong in current_goals.json (year-specific)
GOALS_FIELDS = {
    'iep_goals', 'life_skills_priorities', 'focus_areas',
    'progress_notes'
}


def needs_migration():
    """Check if migration is needed."""
    # Already migrated if current_year.json exists
    if os.path.exists(CURRENT_YEAR_FILE):
        return False
    return True


def migrate_to_year_aware(year='2026-27', stage_key=None):
    """
    Migrate from flat students.json to year-aware directory structure.
    
    Args:
        year: The current school year (e.g. "2026-27")
        stage_key: Teacher's stage (e.g. "elementary") — optional, set separately
    
    Returns:
        dict with migration results, or None if already migrated
    """
    if not needs_migration():
        return None
    
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(STUDENTS_DIR, exist_ok=True)
    
    report = {
        'migrated_at': datetime.now().isoformat(),
        'year': year,
        'students_migrated': 0,
        'students_found': 0,
        'errors': []
    }
    
    # Load existing students (if any)
    students = []
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, 'r') as f:
                students = json.load(f)
            report['students_found'] = len(students)
            
            # Backup the original file before touching it
            shutil.copy2(STUDENTS_FILE, BACKUP_FILE)
        except (json.JSONDecodeError, FileNotFoundError):
            students = []
    
    # Migrate each student to directory structure
    for student in students:
        try:
            student_id = student.get('id')
            if not student_id:
                report['errors'].append(f"Student without ID found: {student.get('name', 'unknown')}")
                continue
            
            _migrate_single_student(student, year)
            report['students_migrated'] += 1
            
        except Exception as e:
            report['errors'].append(f"Error migrating {student.get('name', 'unknown')}: {str(e)}")
    
    # Create current_year.json (this is what marks migration as complete)
    from modules.year_lifecycle import set_current_year
    set_current_year(year)
    
    # Save migration report
    report_path = os.path.join(DATA_DIR, 'migration_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report


def _migrate_single_student(student_data, year):
    """
    Migrate a single student from flat format to directory structure.
    Creates: students/{id}/profile.json, current_goals.json, lifecycle.json
    """
    student_id = student_data['id']
    student_dir = os.path.join(STUDENTS_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)
    
    # Split into profile (persistent) and goals (year-specific)
    profile = {}
    goals = {'year': year}
    
    for key, value in student_data.items():
        if key in PROFILE_FIELDS:
            profile[key] = value
        elif key in GOALS_FIELDS:
            goals[key] = value
        # else: skip (or put in profile as catch-all)
    
    # Ensure profile has the id
    profile['id'] = student_id
    
    # Save profile.json
    with open(os.path.join(student_dir, 'profile.json'), 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Save current_goals.json
    with open(os.path.join(student_dir, 'current_goals.json'), 'w') as f:
        json.dump(goals, f, indent=2)
    
    # Create lifecycle.json
    grade = student_data.get('grade', 'unknown')
    lifecycle = {
        'current_status': 'active',
        'current_grade': grade,
        'current_year': year,
        'entry_year': year,  # Best we can infer — starting tracking now
        'entry_grade': grade,
        'expected_transition_year': 'unknown',  # Will be calculated once stage is set
        'grade_history': [
            {
                'year': year,
                'grade': grade,
                'status': 'in_progress'
            }
        ],
        'held_back_years': [],
        'held_back_count': 0,
        'transition_notes': ''
    }
    
    with open(os.path.join(student_dir, 'lifecycle.json'), 'w') as f:
        json.dump(lifecycle, f, indent=2)


def rollback_migration():
    """
    Emergency rollback — restore from backup if migration went wrong.
    Only works if the backup file exists.
    """
    if os.path.exists(BACKUP_FILE):
        shutil.copy2(BACKUP_FILE, STUDENTS_FILE)
        # Remove the current_year.json to re-trigger migration
        if os.path.exists(CURRENT_YEAR_FILE):
            os.remove(CURRENT_YEAR_FILE)
        return True
    return False
