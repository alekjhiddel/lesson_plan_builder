"""
SPARK - ESY (Extended School Year) Justification Tool
=====================================================
Tracks regression data across school breaks and generates
justification narratives for ESY eligibility in the IEP.

Kentucky context:
- No specific form required — ESY justification lives in the IEP
- Trigger: regression in data after breaks
- March 1st default ESY determination deadline (configurable)
"""

import json
import os
from datetime import datetime, date, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
ESY_DIR = os.path.join(DATA_DIR, 'esy')
BREAK_PERIODS_FILE = os.path.join(ESY_DIR, 'break_periods.json')


def ensure_esy_dir():
    """Ensure the ESY data directory exists."""
    os.makedirs(ESY_DIR, exist_ok=True)


# ============================================================
# Default Kentucky break periods (teacher-adjustable)
# ============================================================

DEFAULT_BREAK_PERIODS = [
    {
        "id": "winter",
        "label": "Winter Break",
        "start": "12-20",
        "end": "01-06",
        "data_window_before_days": 10,
        "data_window_after_days": 10,
    },
    {
        "id": "spring",
        "label": "Spring Break",
        "start": "03-28",
        "end": "04-04",
        "data_window_before_days": 10,
        "data_window_after_days": 10,
    },
    {
        "id": "summer",
        "label": "Summer Break",
        "start": "05-25",
        "end": "08-10",
        "data_window_before_days": 14,
        "data_window_after_days": 14,
    },
]


def get_break_periods():
    """Get configured break periods (or defaults)."""
    ensure_esy_dir()
    if os.path.exists(BREAK_PERIODS_FILE):
        with open(BREAK_PERIODS_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_BREAK_PERIODS


def save_break_periods(periods):
    """Save teacher-configured break periods."""
    ensure_esy_dir()
    with open(BREAK_PERIODS_FILE, 'w') as f:
        json.dump(periods, f, indent=2)


def _get_school_year():
    """Determine current school year (e.g., '2026-2027')."""
    today = date.today()
    if today.month >= 8:
        return today.year, today.year + 1
    else:
        return today.year - 1, today.year


def _parse_break_date(date_str, school_year_start, school_year_end):
    """Parse a MM-DD break date into a full date for the current school year."""
    month, day = date_str.split('-')
    month = int(month)
    day = int(day)
    if month >= 8:
        return date(school_year_start, month, day)
    else:
        return date(school_year_end, month, day)


def get_esy_candidates(students, progress_data_func):
    """
    Scan all students for potential ESY regression.
    
    Args:
        students: List of student dicts from student_manager
        progress_data_func: Function that takes (student_id, goal_id) and returns data points
    
    Returns:
        List of dicts with student info and regression indicators
    """
    candidates = []
    break_periods = get_break_periods()
    year_start, year_end = _get_school_year()
    
    for student in students:
        student_regressions = []
        goals = student.get('iep_goals', [])
        
        for goal in goals:
            goal_id = goal.get('id', goal.get('goal_id', ''))
            if not goal_id:
                continue
                
            for period in break_periods:
                regression = calculate_regression(
                    student.get('id', ''),
                    goal_id,
                    period,
                    progress_data_func,
                    year_start,
                    year_end
                )
                if regression and regression.get('shows_regression'):
                    student_regressions.append({
                        'goal_id': goal_id,
                        'goal_text': goal.get('text', goal.get('template', '')),
                        'break_period': period['label'],
                        'regression_data': regression
                    })
        
        if student_regressions:
            candidates.append({
                'student_id': student.get('id', ''),
                'student_name': student.get('name', ''),
                'regressions': student_regressions,
                'regression_count': len(student_regressions),
            })
    
    return candidates


def calculate_regression(student_id, goal_id, break_period, progress_data_func, year_start, year_end):
    """
    Calculate regression for a specific student/goal across a break period.
    
    Compares average performance in the data window BEFORE the break
    to performance in the data window AFTER the break.
    
    Returns:
        dict with regression analysis, or None if insufficient data
    """
    try:
        break_start = _parse_break_date(break_period['start'], year_start, year_end)
        break_end = _parse_break_date(break_period['end'], year_start, year_end)
    except (ValueError, TypeError):
        return None
    
    before_days = break_period.get('data_window_before_days', 10)
    after_days = break_period.get('data_window_after_days', 10)
    
    before_start = break_start - timedelta(days=before_days)
    after_end = break_end + timedelta(days=after_days)
    
    # Get data for the windows
    before_start_str = before_start.strftime('%Y-%m-%d')
    break_start_str = break_start.strftime('%Y-%m-%d')
    break_end_str = break_end.strftime('%Y-%m-%d')
    after_end_str = after_end.strftime('%Y-%m-%d')
    
    # Get all data points
    all_data = progress_data_func(student_id, goal_id)
    if not all_data:
        return None
    
    # Filter into before and after windows
    before_data = []
    after_data = []
    
    for dp in all_data:
        dp_date = dp.get('date', '')
        if before_start_str <= dp_date < break_start_str:
            before_data.append(dp)
        elif break_end_str < dp_date <= after_end_str:
            after_data.append(dp)
    
    # Need at least 2 data points in each window
    if len(before_data) < 2 or len(after_data) < 2:
        return None
    
    # Calculate averages using normalized percentage
    def avg_percent(data_points):
        percentages = []
        for dp in data_points:
            norm = dp.get('normalized', {})
            pct = norm.get('percentage', None)
            if pct is not None:
                percentages.append(pct)
            elif 'value' in dp:
                percentages.append(float(dp['value']))
        if not percentages:
            return None
        return sum(percentages) / len(percentages)
    
    before_avg = avg_percent(before_data)
    after_avg = avg_percent(after_data)
    
    if before_avg is None or after_avg is None:
        return None
    
    regression_pct = before_avg - after_avg
    shows_regression = regression_pct > 10  # >10% drop = regression
    
    return {
        'shows_regression': shows_regression,
        'before_avg': round(before_avg, 1),
        'after_avg': round(after_avg, 1),
        'regression_pct': round(regression_pct, 1),
        'before_data_points': len(before_data),
        'after_data_points': len(after_data),
        'break_period_label': break_period['label'],
        'before_window': before_start_str + ' to ' + break_start_str,
        'after_window': break_end_str + ' to ' + after_end_str,
    }


def generate_esy_justification(student, regressions):
    """
    Generate ESY justification narrative for a student.
    
    Args:
        student: Student dict
        regressions: List of regression dicts from get_esy_candidates
    
    Returns:
        dict with justification content
    """
    student_name = student.get('name', 'This student')
    
    narrative_parts = []
    narrative_parts.append(
        "Based on data collected before and after school breaks, "
        "{} demonstrates significant regression in the following goal areas:".format(student_name)
    )
    
    goal_details = []
    for reg in regressions:
        rd = reg.get('regression_data', {})
        detail = {
            'goal_text': reg.get('goal_text', 'Goal'),
            'break_period': reg.get('break_period', ''),
            'before_avg': rd.get('before_avg', 0),
            'after_avg': rd.get('after_avg', 0),
            'regression_pct': rd.get('regression_pct', 0),
            'before_points': rd.get('before_data_points', 0),
            'after_points': rd.get('after_data_points', 0),
        }
        goal_details.append(detail)
        
        narrative_parts.append(
            "- {}: Performance dropped from {:.0f}% (pre-break average, {} data points) "
            "to {:.0f}% (post-break average, {} data points) after {}, "
            "representing a {:.0f}% regression.".format(
                detail['goal_text'][:80],
                detail['before_avg'],
                detail['before_points'],
                detail['after_avg'],
                detail['after_points'],
                detail['break_period'],
                detail['regression_pct']
            )
        )
    
    narrative_parts.append("")
    narrative_parts.append(
        "This data indicates that without continued services during extended breaks, "
        "{} is at significant risk of losing skills that require substantial time to recoup. "
        "ESY services are recommended to maintain progress on the identified goals.".format(student_name)
    )
    
    return {
        'student_name': student_name,
        'student_id': student.get('id', ''),
        'generated_date': datetime.now().strftime('%Y-%m-%d'),
        'narrative': '\n'.join(narrative_parts),
        'goal_details': goal_details,
        'total_goals_regressing': len(goal_details),
        'recommendation': 'ESY services recommended' if goal_details else 'Insufficient evidence for ESY',
    }


def format_esy_report(justification):
    """Format ESY justification as a printable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("ESY JUSTIFICATION REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Student: {}".format(justification['student_name']))
    lines.append("Date: {}".format(justification['generated_date']))
    lines.append("Recommendation: {}".format(justification['recommendation']))
    lines.append("")
    lines.append("-" * 60)
    lines.append("REGRESSION DATA SUMMARY")
    lines.append("-" * 60)
    lines.append("")
    lines.append(justification['narrative'])
    lines.append("")
    lines.append("-" * 60)
    lines.append("GOAL-BY-GOAL ANALYSIS")
    lines.append("-" * 60)
    
    for detail in justification.get('goal_details', []):
        lines.append("")
        lines.append("Goal: {}".format(detail['goal_text'][:100]))
        lines.append("  Break Period: {}".format(detail['break_period']))
        lines.append("  Pre-Break Average: {:.0f}% ({} data points)".format(
            detail['before_avg'], detail['before_points']))
        lines.append("  Post-Break Average: {:.0f}% ({} data points)".format(
            detail['after_avg'], detail['after_points']))
        lines.append("  Regression: {:.0f}%".format(detail['regression_pct']))
    
    lines.append("")
    lines.append("=" * 60)
    
    return '\n'.join(lines)
