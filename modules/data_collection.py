"""
SPARK - Data Collection Module
================================
Handles daily data entry, storage, trend analysis, and mastery checking
for IEP goal progress monitoring.

Data Types Supported:
- trial_by_trial: Individual +/- trials per session
- percentage: Percentage correct (0-100)
- frequency_count: Number of occurrences in a time period
- duration: Time in seconds/minutes
- task_analysis_steps: Steps completed independently out of total
- interval_recording: Intervals with/without target behavior

All data stored in data/progress_data.json as append-only log.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

# Path to the data file (relative to app root)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'progress_data.json')

# Supported data collection methods
VALID_METHODS = [
    'trial_by_trial',
    'percentage',
    'frequency_count',
    'duration',
    'task_analysis_steps',
    'interval_recording'
]

# Default mastery criteria
DEFAULT_MASTERY_CONSECUTIVE = 3  # sessions meeting criteria
DEFAULT_MASTERY_THRESHOLD = 80  # percent or equivalent

# PBIS Behavior Categories (v2.1)
PBIS_CATEGORIES = {
    # Expected Behaviors (Positive - track increases)
    'expected_social': {'label': 'Expected: Social interaction', 'direction': 'increase', 'color': '#4caf50'},
    'expected_communication': {'label': 'Expected: Communication attempt', 'direction': 'increase', 'color': '#66bb6a'},
    'expected_task': {'label': 'Expected: Task engagement', 'direction': 'increase', 'color': '#81c784'},
    'expected_transition': {'label': 'Expected: Smooth transition', 'direction': 'increase', 'color': '#a5d6a7'},
    'expected_self_reg': {'label': 'Expected: Self-regulation strategy used', 'direction': 'increase', 'color': '#c8e6c9'},
    # Unexpected Behaviors (Target for reduction)
    'unexpected_aggression': {'label': 'Unexpected: Physical aggression', 'direction': 'decrease', 'color': '#f44336'},
    'unexpected_self_injury': {'label': 'Unexpected: Self-injurious behavior', 'direction': 'decrease', 'color': '#e53935'},
    'unexpected_elopement': {'label': 'Unexpected: Elopement/leaving area', 'direction': 'decrease', 'color': '#ef5350'},
    'unexpected_disruption': {'label': 'Unexpected: Disruption/property destruction', 'direction': 'decrease', 'color': '#e57373'},
    'unexpected_noncompliance': {'label': 'Unexpected: Non-compliance/refusal', 'direction': 'decrease', 'color': '#ef9a9a'},
    'unexpected_stereotypy': {'label': 'Unexpected: Stereotypy (interfering)', 'direction': 'decrease', 'color': '#ffcdd2'},
    # Replacement Behaviors (Teaching targets - track increases)
    'replacement_request': {'label': 'Replacement: Appropriate request (mand)', 'direction': 'increase', 'color': '#2196f3'},
    'replacement_wait': {'label': 'Replacement: Waiting/tolerance', 'direction': 'increase', 'color': '#42a5f5'},
    'replacement_help': {'label': 'Replacement: Asking for help', 'direction': 'increase', 'color': '#64b5f6'},
    'replacement_break': {'label': 'Replacement: Requesting break', 'direction': 'increase', 'color': '#90caf9'},
    'replacement_coping': {'label': 'Replacement: Using coping strategy', 'direction': 'increase', 'color': '#bbdefb'},
}


def get_pbis_categories():
    """Return all PBIS behavior categories."""
    return PBIS_CATEGORIES


def get_pbis_category_label(category_key):
    """Get the display label for a PBIS category."""
    cat = PBIS_CATEGORIES.get(category_key)
    return cat['label'] if cat else category_key




def _ensure_data_file():
    """Create data directory and file if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)


def _load_data():
    """Load all data points from the JSON file."""
    _ensure_data_file()
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_data(data):
    """Save data points to the JSON file (full rewrite of append-only log)."""
    _ensure_data_file()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def _normalize_value(value, method):
    """
    Normalize a data value based on collection method.
    Returns a standardized dict with raw value and computed percentage.
    """
    if method == 'trial_by_trial':
        # value should be a list of +/- or True/False
        # e.g., [True, False, True, True, False] or "++-+-"
        if isinstance(value, str):
            trials = [c == '+' for c in value.replace(' ', '')]
        elif isinstance(value, list):
            trials = [bool(t) for t in value]
        else:
            trials = []
        correct = sum(trials)
        total = len(trials)
        pct = (correct / total * 100) if total > 0 else 0
        return {
            'trials': trials,
            'correct': correct,
            'total': total,
            'percentage': round(pct, 1)
        }

    elif method == 'percentage':
        # Direct percentage value
        pct = float(value) if value is not None else 0
        return {
            'percentage': round(min(max(pct, 0), 100), 1)
        }

    elif method == 'frequency_count':
        # Number of occurrences; may include observation period
        if isinstance(value, dict):
            count = int(value.get('count', 0))
            period_minutes = int(value.get('period_minutes', 60))
        else:
            count = int(value)
            period_minutes = 60  # default 1 hour
        rate = count / period_minutes if period_minutes > 0 else 0
        return {
            'count': count,
            'period_minutes': period_minutes,
            'rate_per_minute': round(rate, 3)
        }

    elif method == 'duration':
        # Time in seconds
        if isinstance(value, dict):
            seconds = int(value.get('seconds', 0))
        else:
            seconds = int(value)
        return {
            'seconds': seconds,
            'minutes': round(seconds / 60, 1),
            'formatted': f"{seconds // 60}m {seconds % 60}s"
        }

    elif method == 'task_analysis_steps':
        # Steps completed independently out of total
        if isinstance(value, dict):
            completed = int(value.get('completed', 0))
            total = int(value.get('total', 1))
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            completed, total = int(value[0]), int(value[1])
        else:
            completed = int(value)
            total = completed  # assume all steps if not specified
        pct = (completed / total * 100) if total > 0 else 0
        return {
            'completed': completed,
            'total': total,
            'percentage': round(pct, 1)
        }

    elif method == 'interval_recording':
        # Intervals with target behavior out of total intervals
        if isinstance(value, dict):
            intervals_with = int(value.get('intervals_with', 0))
            total_intervals = int(value.get('total_intervals', 1))
        elif isinstance(value, str):
            # Parse "++--+-" style
            intervals_with = value.count('+')
            total_intervals = len(value.replace(' ', ''))
        else:
            intervals_with = int(value)
            total_intervals = intervals_with
        pct = (intervals_with / total_intervals * 100) if total_intervals > 0 else 0
        return {
            'intervals_with': intervals_with,
            'total_intervals': total_intervals,
            'percentage': round(pct, 1)
        }

    else:
        # Unknown method - store raw
        return {'raw_value': value}


def add_data_point(student_id, goal_id, date, value, method, notes="", behavior_category=''):
    """
    Record a single data point for a student's IEP goal.

    Args:
        student_id (str): Unique student identifier
        goal_id (str): Unique goal identifier
        date (str): Date of observation (YYYY-MM-DD)
        value: Data value (format depends on method)
        method (str): One of VALID_METHODS
        notes (str): Optional observation notes

    Returns:
        dict: The saved data point with computed values

    Raises:
        ValueError: If method is not valid
    """
    if method not in VALID_METHODS:
        raise ValueError(
            f"Invalid method '{method}'. Must be one of: {VALID_METHODS}"
        )

    # Parse and validate date
    if isinstance(date, datetime):
        date_str = date.strftime('%Y-%m-%d')
    else:
        date_str = str(date)
        # Validate format
        datetime.strptime(date_str, '%Y-%m-%d')

    # Normalize the value
    normalized = _normalize_value(value, method)

    # Build the data point
    data_point = {
        'id': f"dp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{student_id}_{goal_id}",
        'student_id': str(student_id),
        'goal_id': str(goal_id),
        'date': date_str,
        'method': method,
        'raw_value': value,
        'normalized': normalized,
        'notes': notes,
        'recorded_at': datetime.now().isoformat(),
        'recorded_by': 'teacher'  # Could be expanded for multi-user
    }

    # Append to log
    data = _load_data()
    data.append(data_point)
    _save_data(data)

    # Check for mastery alert
    mastery_check = check_mastery(student_id, goal_id)
    if mastery_check.get('mastered'):
        data_point['mastery_alert'] = True
        data_point['mastery_message'] = (
            f"🎉 MASTERY ALERT: Student met criteria for "
            f"{mastery_check['consecutive_sessions']} consecutive sessions!"
        )

    return data_point


def get_goal_data(student_id, goal_id, date_range=None):
    """
    Retrieve all data points for a specific goal.

    Args:
        student_id (str): Student identifier
        goal_id (str): Goal identifier
        date_range (tuple, optional): (start_date, end_date) as 'YYYY-MM-DD' strings

    Returns:
        list: Data points sorted by date, oldest first
    """
    data = _load_data()

    # Filter by student and goal
    filtered = [
        dp for dp in data
        if dp['student_id'] == str(student_id)
        and dp['goal_id'] == str(goal_id)
    ]

    # Apply date range filter
    if date_range:
        start_date, end_date = date_range
        filtered = [
            dp for dp in filtered
            if start_date <= dp['date'] <= end_date
        ]

    # Sort by date
    filtered.sort(key=lambda x: x['date'])
    return filtered


def get_student_data_summary(student_id):
    """
    Get an overview of all goals and recent data for a student.

    Args:
        student_id (str): Student identifier

    Returns:
        dict: Summary with goal-level statistics
    """
    data = _load_data()

    # Filter by student
    student_data = [
        dp for dp in data
        if dp['student_id'] == str(student_id)
    ]

    if not student_data:
        return {
            'student_id': student_id,
            'total_data_points': 0,
            'goals': {},
            'last_entry_date': None,
            'weekly_entries': 0
        }

    # Group by goal
    goals = {}
    for dp in student_data:
        gid = dp['goal_id']
        if gid not in goals:
            goals[gid] = {
                'goal_id': gid,
                'method': dp['method'],
                'total_points': 0,
                'first_date': dp['date'],
                'last_date': dp['date'],
                'recent_values': []
            }
        goals[gid]['total_points'] += 1
        goals[gid]['last_date'] = max(goals[gid]['last_date'], dp['date'])
        goals[gid]['first_date'] = min(goals[gid]['first_date'], dp['date'])

    # Get recent values for each goal (last 5)
    for gid in goals:
        goal_data = sorted(
            [dp for dp in student_data if dp['goal_id'] == gid],
            key=lambda x: x['date'],
            reverse=True
        )[:5]
        goals[gid]['recent_values'] = [
            {
                'date': dp['date'],
                'normalized': dp['normalized']
            }
            for dp in goal_data
        ]

    # Weekly entries count
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_start_str = week_start.strftime('%Y-%m-%d')
    weekly_entries = sum(
        1 for dp in student_data
        if dp['date'] >= week_start_str
    )

    return {
        'student_id': student_id,
        'total_data_points': len(student_data),
        'goals': goals,
        'last_entry_date': max(dp['date'] for dp in student_data),
        'weekly_entries': weekly_entries,
        'weeks_of_data': _calculate_weeks(student_data)
    }


def _calculate_weeks(data_points):
    """Calculate how many unique weeks have data."""
    weeks = set()
    for dp in data_points:
        d = datetime.strptime(dp['date'], '%Y-%m-%d').date()
        week_start = d - timedelta(days=d.weekday())
        weeks.add(week_start)
    return len(weeks)


def calculate_progress(student_id, goal_id):
    """
    Compare current performance to baseline and determine trend.

    Uses the first 3 data points as baseline and the last 3 as current.
    Trend is calculated using a simple linear regression over all points.

    Args:
        student_id (str): Student identifier
        goal_id (str): Goal identifier

    Returns:
        dict: Progress analysis including baseline, current, trend, and change
    """
    data = get_goal_data(student_id, goal_id)

    if not data:
        return {
            'student_id': student_id,
            'goal_id': goal_id,
            'status': 'no_data',
            'message': 'No data collected yet for this goal.'
        }

    # Extract percentage values for comparison
    percentages = []
    for dp in data:
        norm = dp.get('normalized', {})
        if 'percentage' in norm:
            percentages.append(norm['percentage'])
        elif 'count' in norm:
            # For frequency, use raw count
            percentages.append(norm['count'])
        elif 'seconds' in norm:
            # For duration, use seconds
            percentages.append(norm['seconds'])

    if len(percentages) < 2:
        return {
            'student_id': student_id,
            'goal_id': goal_id,
            'status': 'insufficient_data',
            'data_points': len(percentages),
            'message': 'Need at least 2 data points to calculate progress.'
        }

    # Baseline = average of first 3 (or fewer) data points
    baseline_points = percentages[:3]
    baseline = sum(baseline_points) / len(baseline_points)

    # Current = average of last 3 data points
    current_points = percentages[-3:]
    current = sum(current_points) / len(current_points)

    # Overall trend using simple slope
    n = len(percentages)
    if n >= 3:
        # Calculate slope using least squares
        x_mean = (n - 1) / 2
        y_mean = sum(percentages) / n
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(percentages))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0

        # Determine trend direction
        if slope > 1.0:
            trend = 'progressing'
        elif slope < -1.0:
            trend = 'regressing'
        else:
            trend = 'maintaining'
    else:
        slope = current - baseline
        trend = 'progressing' if slope > 0 else ('regressing' if slope < 0 else 'maintaining')

    # Calculate change
    change = current - baseline
    change_pct = (change / baseline * 100) if baseline != 0 else 0

    return {
        'student_id': student_id,
        'goal_id': goal_id,
        'status': 'calculated',
        'baseline': round(baseline, 1),
        'current_level': round(current, 1),
        'change': round(change, 1),
        'change_percent': round(change_pct, 1),
        'trend': trend,
        'slope': round(slope, 3),
        'total_sessions': n,
        'date_range': {
            'first': data[0]['date'],
            'last': data[-1]['date']
        },
        'method': data[0].get('method', 'unknown')
    }


def check_mastery(student_id, goal_id, threshold=None, consecutive=None):
    """
    Check if a student has met mastery criteria for consecutive sessions.

    Default: 80% or above for 3 consecutive sessions.

    Args:
        student_id (str): Student identifier
        goal_id (str): Goal identifier
        threshold (float, optional): Mastery threshold (default 80)
        consecutive (int, optional): Required consecutive sessions (default 3)

    Returns:
        dict: Mastery status with details
    """
    if threshold is None:
        threshold = DEFAULT_MASTERY_THRESHOLD
    if consecutive is None:
        consecutive = DEFAULT_MASTERY_CONSECUTIVE

    data = get_goal_data(student_id, goal_id)

    if not data:
        return {
            'mastered': False,
            'consecutive_sessions': 0,
            'threshold': threshold,
            'required_consecutive': consecutive,
            'message': 'No data available.'
        }

    # Extract performance values
    performances = []
    for dp in data:
        norm = dp.get('normalized', {})
        if 'percentage' in norm:
            performances.append({
                'date': dp['date'],
                'value': norm['percentage'],
                'meets_criteria': norm['percentage'] >= threshold
            })
        elif 'count' in norm:
            # For frequency count, mastery might mean BELOW threshold
            # (for behavior reduction goals)
            performances.append({
                'date': dp['date'],
                'value': norm['count'],
                'meets_criteria': norm['count'] <= threshold
            })

    if not performances:
        return {
            'mastered': False,
            'consecutive_sessions': 0,
            'threshold': threshold,
            'required_consecutive': consecutive,
            'message': 'Cannot determine mastery from available data type.'
        }

    # Check consecutive sessions meeting criteria (from most recent)
    consecutive_met = 0
    for perf in reversed(performances):
        if perf['meets_criteria']:
            consecutive_met += 1
        else:
            break

    mastered = consecutive_met >= consecutive

    result = {
        'mastered': mastered,
        'consecutive_sessions': consecutive_met,
        'threshold': threshold,
        'required_consecutive': consecutive,
        'last_session': performances[-1] if performances else None,
        'total_sessions': len(performances)
    }

    if mastered:
        result['message'] = (
            f"🎉 MASTERED! Student met criteria ({threshold}%) for "
            f"{consecutive_met} consecutive sessions. "
            f"Consider advancing to next goal or increasing criteria."
        )
        result['mastery_date'] = performances[-1]['date']
    else:
        remaining = consecutive - consecutive_met
        result['message'] = (
            f"Not yet mastered. {consecutive_met}/{consecutive} consecutive "
            f"sessions at criteria. Need {remaining} more."
        )

    return result


def generate_data_sheet(student_id, goal_ids, student_name="", goal_details=None):
    """
    Create data for a printable data collection sheet.

    Args:
        student_id (str): Student identifier
        goal_ids (list): List of goal IDs to include
        student_name (str): Student's display name
        goal_details (dict, optional): Goal metadata {goal_id: {text, method, target}}

    Returns:
        dict: Structured data for rendering a printable sheet
    """
    if goal_details is None:
        goal_details = {}

    today = datetime.now().date()
    # Generate dates for next 2 weeks (10 school days)
    school_days = []
    current = today
    while len(school_days) < 10:
        if current.weekday() < 5:  # Monday-Friday
            school_days.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)

    sheets = []
    for goal_id in goal_ids:
        goal_info = goal_details.get(goal_id, {})
        method = goal_info.get('method', 'percentage')
        goal_text = goal_info.get('text', f'Goal {goal_id}')
        target = goal_info.get('target', '80%')

        # Build appropriate data sheet format
        if method == 'trial_by_trial':
            sheet_type = 'trial_grid'
            columns = school_days
            rows = [f"Trial {i+1}" for i in range(10)]
            instructions = "Mark + for correct, - for incorrect"

        elif method == 'percentage':
            sheet_type = 'percentage_log'
            columns = school_days
            rows = ['Score', 'Total Possible', 'Percentage', 'Notes']
            instructions = "Record correct/total and calculate percentage"

        elif method == 'frequency_count':
            sheet_type = 'tally_sheet'
            columns = school_days
            rows = ['Tally Marks', 'Total Count', 'Time Period', 'Rate', 'Notes']
            instructions = "Use tally marks (||||) to count occurrences"

        elif method == 'duration':
            sheet_type = 'duration_log'
            columns = school_days
            rows = ['Start Time', 'End Time', 'Duration', 'Activity', 'Notes']
            instructions = "Record start/end times; calculate total duration"

        elif method == 'task_analysis_steps':
            # Get steps from goal details or use generic
            steps = goal_info.get('steps', [f"Step {i+1}" for i in range(8)])
            sheet_type = 'task_analysis'
            columns = school_days[:5]  # Only 5 days for wider format
            rows = steps + ['Total Independent', 'Percentage']
            instructions = "Mark I=Independent, V=Verbal, M=Model, P=Physical, X=Not attempted"

        elif method == 'interval_recording':
            sheet_type = 'interval_grid'
            # 15 intervals per session
            columns = [f"Int {i+1}" for i in range(15)]
            rows = school_days[:5]  # 5 days, intervals as columns
            instructions = "Mark + if behavior occurred during interval, - if not"

        else:
            sheet_type = 'generic'
            columns = school_days
            rows = ['Value', 'Notes']
            instructions = "Record data value for each session"

        sheets.append({
            'goal_id': goal_id,
            'goal_text': goal_text,
            'method': method,
            'target': target,
            'sheet_type': sheet_type,
            'columns': columns,
            'rows': rows,
            'instructions': instructions
        })

    return {
        'student_id': student_id,
        'student_name': student_name,
        'generated_date': today.strftime('%Y-%m-%d'),
        'school_days': school_days,
        'sheets': sheets
    }


def get_weekly_collection_status(student_id, goal_ids=None):
    """
    Check how much data has been collected this week for a student.
    Useful for showing visual indicators on the data entry page.

    Args:
        student_id (str): Student identifier
        goal_ids (list, optional): Specific goals to check

    Returns:
        dict: Collection status per goal for current week
    """
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=4)  # Friday

    date_range = (
        week_start.strftime('%Y-%m-%d'),
        week_end.strftime('%Y-%m-%d')
    )

    data = _load_data()
    student_data = [
        dp for dp in data
        if dp['student_id'] == str(student_id)
        and date_range[0] <= dp['date'] <= date_range[1]
    ]

    if goal_ids:
        student_data = [
            dp for dp in student_data
            if dp['goal_id'] in [str(g) for g in goal_ids]
        ]

    # Group by goal
    status = {}
    goals_seen = set(dp['goal_id'] for dp in student_data)

    if goal_ids:
        all_goals = [str(g) for g in goal_ids]
    else:
        all_goals = list(goals_seen)

    # Calculate school days elapsed this week
    school_days_elapsed = min(today.weekday() + 1, 5)
    total_school_days = 5

    for gid in all_goals:
        goal_entries = [dp for dp in student_data if dp['goal_id'] == gid]
        days_with_data = len(set(dp['date'] for dp in goal_entries))

        status[gid] = {
            'entries_this_week': len(goal_entries),
            'days_with_data': days_with_data,
            'school_days_elapsed': school_days_elapsed,
            'total_school_days': total_school_days,
            'completion_pct': round(days_with_data / school_days_elapsed * 100)
                             if school_days_elapsed > 0 else 0,
            'on_track': days_with_data >= school_days_elapsed - 1
        }

    return {
        'student_id': student_id,
        'week_start': date_range[0],
        'week_end': date_range[1],
        'goals': status,
        'overall_entries': len(student_data)
    }


def delete_data_point(data_point_id):
    """
    Remove a data point by ID (soft delete - marks as deleted).

    Args:
        data_point_id (str): The data point ID to delete

    Returns:
        bool: True if found and deleted
    """
    data = _load_data()
    for dp in data:
        if dp.get('id') == data_point_id:
            dp['deleted'] = True
            dp['deleted_at'] = datetime.now().isoformat()
            _save_data(data)
            return True
    return False


def get_mastery_alerts(student_ids=None):
    """
    Check all students/goals for mastery alerts.
    Useful for dashboard notifications.

    Args:
        student_ids (list, optional): Specific students to check

    Returns:
        list: Goals that have been mastered
    """
    data = _load_data()

    # Get unique student-goal combinations
    combinations = set()
    for dp in data:
        if dp.get('deleted'):
            continue
        if student_ids and dp['student_id'] not in [str(s) for s in student_ids]:
            continue
        combinations.add((dp['student_id'], dp['goal_id']))

    alerts = []
    for student_id, goal_id in combinations:
        result = check_mastery(student_id, goal_id)
        if result['mastered']:
            alerts.append({
                'student_id': student_id,
                'goal_id': goal_id,
                'mastery_date': result.get('mastery_date'),
                'consecutive_sessions': result['consecutive_sessions'],
                'message': result['message']
            })

    return alerts
