"""
SPARK - Goal Mastery & Next Goal Recommendations
=================================================
Tracks when students master IEP goals, suggests next goals from the
goal bank, and celebrates achievements.

Key behaviors:
- Mastery criteria is configurable PER STUDENT PER GOAL
- Default: 80% across 3 consecutive sessions
- When mastery is detected: flag it, suggest next goal, note ARC should be convened
- Pulls next-goal suggestions from goal bank (same domain, next level up)
- Also allows custom goal writing
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
MASTERY_DIR = os.path.join(DATA_DIR, 'mastery')
CRITERIA_FILE = os.path.join(MASTERY_DIR, 'criteria.json')
MASTERY_LOG_FILE = os.path.join(MASTERY_DIR, 'mastery_log.json')


def ensure_mastery_dir():
    """Ensure the mastery data directory exists."""
    os.makedirs(MASTERY_DIR, exist_ok=True)


# ============================================================
# Mastery Criteria (per student per goal)
# ============================================================

DEFAULT_THRESHOLD = 80  # percent
DEFAULT_CONSECUTIVE = 3  # sessions


def _load_criteria():
    """Load saved mastery criteria."""
    ensure_mastery_dir()
    if os.path.exists(CRITERIA_FILE):
        with open(CRITERIA_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_criteria(data):
    """Save mastery criteria."""
    ensure_mastery_dir()
    with open(CRITERIA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_mastery_criteria(student_id, goal_id):
    """
    Get mastery criteria for a specific student/goal.
    Returns dict with 'threshold' and 'consecutive'.
    Falls back to defaults if not customized.
    """
    criteria = _load_criteria()
    key = "{}__{}".format(student_id, goal_id)
    if key in criteria:
        return criteria[key]
    return {
        'threshold': DEFAULT_THRESHOLD,
        'consecutive': DEFAULT_CONSECUTIVE,
        'customized': False
    }


def set_mastery_criteria(student_id, goal_id, threshold, consecutive):
    """
    Save custom mastery criteria for a student/goal.
    
    Args:
        student_id: Student identifier
        goal_id: Goal identifier
        threshold: Percent threshold (e.g., 60, 80, 90)
        consecutive: Number of consecutive sessions required
    """
    criteria = _load_criteria()
    key = "{}__{}".format(student_id, goal_id)
    criteria[key] = {
        'threshold': int(threshold),
        'consecutive': int(consecutive),
        'customized': True,
        'updated': datetime.now().strftime('%Y-%m-%d')
    }
    _save_criteria(criteria)


# ============================================================
# Mastery Log (celebrations!)
# ============================================================

def _load_mastery_log():
    """Load the mastery event log."""
    ensure_mastery_dir()
    if os.path.exists(MASTERY_LOG_FILE):
        with open(MASTERY_LOG_FILE, 'r') as f:
            return json.load(f)
    return []


def _save_mastery_log(log):
    """Save the mastery event log."""
    ensure_mastery_dir()
    with open(MASTERY_LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)


def mark_goal_mastered(student_id, student_name, goal_id, goal_text, mastery_date=None):
    """
    Record that a student has mastered a goal.
    
    Args:
        student_id: Student identifier
        student_name: Student display name
        goal_id: Goal identifier
        goal_text: Goal description text
        mastery_date: Date of mastery (defaults to today)
    """
    log = _load_mastery_log()
    
    # Don't duplicate
    for entry in log:
        if entry['student_id'] == student_id and entry['goal_id'] == goal_id:
            return  # Already recorded
    
    log.append({
        'student_id': student_id,
        'student_name': student_name,
        'goal_id': goal_id,
        'goal_text': goal_text[:200],
        'mastery_date': mastery_date or datetime.now().strftime('%Y-%m-%d'),
        'recorded_at': datetime.now().isoformat(),
        'arc_notified': False,
    })
    _save_mastery_log(log)


def get_mastery_celebrations(limit=10):
    """Get recent mastery events for the celebration dashboard."""
    log = _load_mastery_log()
    # Sort by mastery_date descending
    log.sort(key=lambda x: x.get('mastery_date', ''), reverse=True)
    return log[:limit]


def get_mastered_goals_for_student(student_id):
    """Get all mastered goals for a specific student."""
    log = _load_mastery_log()
    return [entry for entry in log if entry['student_id'] == student_id]


# ============================================================
# Mastery Checking (integrates with data_collection)
# ============================================================

def check_all_mastery(students, get_goal_data_func):
    """
    Scan all students' goals for mastery.
    
    Args:
        students: List of student dicts
        get_goal_data_func: Function(student_id, goal_id) → list of data points
    
    Returns:
        dict with 'mastered' (newly mastered), 'approaching' (close to mastery)
    """
    mastered = []
    approaching = []
    already_mastered = _load_mastery_log()
    already_ids = set("{}__{}".format(m['student_id'], m['goal_id']) for m in already_mastered)
    
    for student in students:
        student_id = student.get('id', '')
        goals = student.get('iep_goals', [])
        
        for goal in goals:
            goal_id = goal.get('id', goal.get('goal_id', ''))
            if not goal_id:
                continue
            
            # Skip already-mastered goals
            key = "{}__{}".format(student_id, goal_id)
            if key in already_ids:
                continue
            
            criteria = get_mastery_criteria(student_id, goal_id)
            threshold = criteria['threshold']
            consecutive = criteria['consecutive']
            
            # Get data and check
            data = get_goal_data_func(student_id, goal_id)
            if not data:
                continue
            
            result = _check_mastery_from_data(data, threshold, consecutive)
            
            if result['mastered']:
                mastered.append({
                    'student_id': student_id,
                    'student_name': student.get('name', ''),
                    'goal_id': goal_id,
                    'goal_text': goal.get('text', goal.get('template', '')),
                    'criteria': criteria,
                    'consecutive_met': result['consecutive_met'],
                })
            elif result['approaching']:
                approaching.append({
                    'student_id': student_id,
                    'student_name': student.get('name', ''),
                    'goal_id': goal_id,
                    'goal_text': goal.get('text', goal.get('template', '')),
                    'criteria': criteria,
                    'consecutive_met': result['consecutive_met'],
                    'sessions_needed': consecutive - result['consecutive_met'],
                })
    
    return {
        'mastered': mastered,
        'approaching': approaching,
    }


def _check_mastery_from_data(data_points, threshold, consecutive):
    """
    Check if the most recent data points meet mastery criteria.
    
    Returns:
        dict with 'mastered' (bool), 'approaching' (bool), 'consecutive_met' (int)
    """
    if not data_points:
        return {'mastered': False, 'approaching': False, 'consecutive_met': 0}
    
    # Sort by date descending (most recent first)
    sorted_data = sorted(data_points, key=lambda x: x.get('date', ''), reverse=True)
    
    # Count consecutive sessions meeting threshold
    consecutive_met = 0
    for dp in sorted_data:
        norm = dp.get('normalized', {})
        pct = norm.get('percentage', None)
        if pct is None and 'value' in dp:
            try:
                pct = float(dp['value'])
            except (ValueError, TypeError):
                break
        
        if pct is not None and pct >= threshold:
            consecutive_met += 1
        else:
            break
    
    mastered = consecutive_met >= consecutive
    approaching = not mastered and consecutive_met >= (consecutive - 1) and consecutive_met > 0
    
    return {
        'mastered': mastered,
        'approaching': approaching,
        'consecutive_met': consecutive_met,
    }


# ============================================================
# Next Goal Suggestions (from goal bank)
# ============================================================

def get_suggested_next_goals(mastered_goal_id, goal_bank_data):
    """
    Suggest next goals from the goal bank based on the mastered goal.
    
    Finds goals in the same domain/skill area at the next difficulty level.
    
    Args:
        mastered_goal_id: The goal ID that was mastered
        goal_bank_data: The full GOAL_BANK dict
    
    Returns:
        List of suggested goal dicts
    """
    suggestions = []
    mastered_goal = None
    mastered_domain = None
    mastered_area = None
    mastered_level = None
    
    # Find the mastered goal in the bank
    for domain_key, domain_data in goal_bank_data.items():
        if 'skill_areas' not in domain_data:
            continue
        for area_key, area_data in domain_data['skill_areas'].items():
            for goal in area_data.get('goals', []):
                if goal.get('id') == mastered_goal_id:
                    mastered_goal = goal
                    mastered_domain = domain_key
                    mastered_area = area_key
                    mastered_level = goal.get('level', 1)
                    break
            if mastered_goal:
                break
        if mastered_goal:
            break
    
    if not mastered_goal or not mastered_domain:
        return []
    
    # Find goals at the next level in the same skill area
    next_level = mastered_level + 1
    domain_data = goal_bank_data.get(mastered_domain, {})
    area_data = domain_data.get('skill_areas', {}).get(mastered_area, {})
    
    for goal in area_data.get('goals', []):
        if goal.get('level', 0) == next_level and goal.get('id') != mastered_goal_id:
            suggestions.append({
                'id': goal['id'],
                'text': goal.get('template', ''),
                'level': goal.get('level'),
                'domain': mastered_domain,
                'skill_area': mastered_area,
                'source': 'goal_bank',
            })
    
    # If no next-level goals in same area, look at same domain, different area
    if not suggestions:
        for area_key, area_data in domain_data.get('skill_areas', {}).items():
            if area_key == mastered_area:
                continue
            for goal in area_data.get('goals', []):
                if goal.get('level', 0) in (mastered_level, next_level):
                    suggestions.append({
                        'id': goal['id'],
                        'text': goal.get('template', ''),
                        'level': goal.get('level'),
                        'domain': mastered_domain,
                        'skill_area': area_key,
                        'source': 'goal_bank_related',
                    })
            if len(suggestions) >= 3:
                break
    
    return suggestions[:5]  # Max 5 suggestions
