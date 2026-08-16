"""
SPARK - Progress Reports Module
=================================
Generates quarterly progress reports for IEP goals.
Kentucky requirement: Reports concurrent with report cards (quarterly).

Features:
- Full progress report generation for all goals
- Trend analysis with visual indicators
- ChatGPT prompt generation for narrative writing
- On-track determination for annual goals
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

from .data_collection import (
    get_goal_data,
    calculate_progress,
    check_mastery,
    get_student_data_summary
)

# Kentucky reporting periods (aligned with report cards)
REPORTING_PERIODS = {
    'Q1': {'name': 'Quarter 1', 'start_month': 8, 'end_month': 10},
    'Q2': {'name': 'Quarter 2', 'start_month': 10, 'end_month': 12},
    'Q3': {'name': 'Quarter 3', 'start_month': 1, 'end_month': 3},
    'Q4': {'name': 'Quarter 4', 'start_month': 3, 'end_month': 5},
}

# Trend indicators
TREND_LABELS = {
    'progressing': '📈 Progressing',
    'maintaining': '➡️ Maintaining',
    'regressing': '📉 Regressing',
}


def _get_reporting_dates(reporting_period, school_year=None):
    """
    Get start and end dates for a reporting period.

    Args:
        reporting_period (str): 'Q1', 'Q2', 'Q3', or 'Q4'
        school_year (str, optional): e.g., '2025-2026'

    Returns:
        tuple: (start_date, end_date) as 'YYYY-MM-DD' strings
    """
    if school_year:
        start_year = int(school_year.split('-')[0])
    else:
        now = datetime.now()
        start_year = now.year if now.month >= 8 else now.year - 1

    period = REPORTING_PERIODS.get(reporting_period)
    if not period:
        raise ValueError(f"Invalid reporting period: {reporting_period}")

    start_month = period['start_month']
    end_month = period['end_month']

    # Determine year for start and end
    if start_month >= 8:
        start_date_year = start_year
    else:
        start_date_year = start_year + 1

    if end_month >= 8:
        end_date_year = start_year
    else:
        end_date_year = start_year + 1

    start_date = f"{start_date_year}-{start_month:02d}-01"

    # End of the end month
    if end_month == 12:
        end_date = f"{end_date_year}-12-31"
    else:
        # Last day of end month
        import calendar
        last_day = calendar.monthrange(end_date_year, end_month)[1]
        end_date = f"{end_date_year}-{end_month:02d}-{last_day:02d}"

    return start_date, end_date


def generate_progress_report(student_id, reporting_period, student_info=None, goals_info=None):
    """
    Generate a full quarterly progress report for all of a student's goals.

    Args:
        student_id (str): Student identifier
        reporting_period (str): 'Q1', 'Q2', 'Q3', or 'Q4'
        student_info (dict, optional): Student metadata {name, grade, teacher, case_manager}
        goals_info (dict, optional): Goal metadata {goal_id: {text, baseline, target, area, method}}

    Returns:
        dict: Complete progress report data
    """
    if student_info is None:
        student_info = {'name': f'Student {student_id}'}
    if goals_info is None:
        goals_info = {}

    # Get reporting period dates
    start_date, end_date = _get_reporting_dates(reporting_period)

    # Get overall student summary
    summary = get_student_data_summary(student_id)

    # Build report for each goal
    goal_reports = []
    for goal_id, goal_info in goals_info.items():
        goal_report = _generate_goal_report(
            student_id, goal_id, goal_info,
            start_date, end_date
        )
        goal_reports.append(goal_report)

    # If no goals_info provided, try to find goals from data
    if not goals_info and summary.get('goals'):
        for goal_id in summary['goals']:
            goal_report = _generate_goal_report(
                student_id, goal_id, {},
                start_date, end_date
            )
            goal_reports.append(goal_report)

    # Overall assessment
    progressing_count = sum(
        1 for g in goal_reports if g['trend'] == 'progressing'
    )
    on_track_count = sum(
        1 for g in goal_reports if g.get('on_track_for_annual')
    )

    report = {
        'report_id': f"pr_{student_id}_{reporting_period}_{datetime.now().strftime('%Y%m%d')}",
        'student_id': student_id,
        'student_info': student_info,
        'reporting_period': reporting_period,
        'period_name': REPORTING_PERIODS[reporting_period]['name'],
        'date_range': {'start': start_date, 'end': end_date},
        'generated_date': datetime.now().strftime('%Y-%m-%d'),
        'goals': goal_reports,
        'summary': {
            'total_goals': len(goal_reports),
            'progressing': progressing_count,
            'on_track': on_track_count,
            'total_data_points': summary.get('total_data_points', 0)
        },
        'kentucky_compliance': {
            'concurrent_with_report_card': True,
            'all_goals_addressed': len(goal_reports) == len(goals_info) if goals_info else True,
            'parent_notification': True
        }
    }

    return report


def _generate_goal_report(student_id, goal_id, goal_info, start_date, end_date):
    """Generate report section for a single goal."""

    # Get data for this period
    period_data = get_goal_data(student_id, goal_id, (start_date, end_date))

    # Get all-time progress
    progress = calculate_progress(student_id, goal_id)

    # Check mastery
    mastery = check_mastery(student_id, goal_id)

    # Extract goal metadata
    goal_text = goal_info.get('text', f'Goal {goal_id}')
    baseline_value = goal_info.get('baseline', progress.get('baseline', 'N/A'))
    target_value = goal_info.get('target', 80)
    goal_area = goal_info.get('area', 'Academic')
    method = goal_info.get('method', progress.get('method', 'percentage'))

    # Current level from this period
    if period_data:
        recent_values = []
        for dp in period_data[-5:]:
            norm = dp.get('normalized', {})
            if 'percentage' in norm:
                recent_values.append(norm['percentage'])
        current_level = (
            round(sum(recent_values) / len(recent_values), 1)
            if recent_values else 'N/A'
        )
    else:
        current_level = progress.get('current_level', 'N/A')

    # Determine trend
    trend = progress.get('trend', 'maintaining')

    # On track for annual goal?
    on_track = _determine_on_track(
        baseline_value, current_level, target_value, trend
    )

    return {
        'goal_id': goal_id,
        'goal_text': goal_text,
        'goal_area': goal_area,
        'method': method,
        'baseline': baseline_value,
        'current_level': current_level,
        'target': target_value,
        'trend': trend,
        'trend_label': TREND_LABELS.get(trend, trend),
        'on_track_for_annual': on_track,
        'mastery_status': mastery,
        'data_points_this_period': len(period_data),
        'progress_details': progress,
        'period_dates': {
            'first_data': period_data[0]['date'] if period_data else None,
            'last_data': period_data[-1]['date'] if period_data else None
        }
    }


def _determine_on_track(baseline, current, target, trend):
    """
    Determine if student is on track to meet annual goal.

    Simple heuristic: If progressing and current > halfway between
    baseline and target, likely on track.
    """
    try:
        baseline_val = float(baseline) if baseline != 'N/A' else 0
        current_val = float(current) if current != 'N/A' else 0
        target_val = float(target)
    except (ValueError, TypeError):
        return None  # Can't determine

    if current_val >= target_val:
        return True  # Already met!

    if trend == 'regressing':
        return False

    # Calculate progress toward target
    total_gap = target_val - baseline_val
    if total_gap <= 0:
        return True

    progress_made = current_val - baseline_val
    progress_pct = progress_made / total_gap

    # If progressing and at least 25% of the way there by mid-year,
    # or 50% by Q3, consider on track
    if trend == 'progressing' and progress_pct >= 0.25:
        return True
    elif trend == 'maintaining' and progress_pct >= 0.5:
        return True

    return False


def generate_progress_prompt(student, goals_with_data):
    """
    Generate a ChatGPT prompt for writing progress report narratives.

    This creates a structured prompt that can be pasted into ChatGPT
    or sent via API to generate parent-friendly narrative descriptions.

    Args:
        student (dict): Student info {name, grade, disability, strengths}
        goals_with_data (list): List of goal reports from generate_progress_report

    Returns:
        str: Formatted prompt for ChatGPT
    """
    student_name = student.get('name', 'the student')
    grade = student.get('grade', '')
    disability = student.get('disability', '')
    strengths = student.get('strengths', '')

    prompt = f"""You are a special education teacher in Kentucky writing quarterly IEP progress reports for parents. Write professional, clear, and encouraging narratives that accurately reflect data.

STUDENT INFORMATION:
- Name: {student_name}
- Grade: {grade}
- Primary Disability Category: {disability}
- Strengths: {strengths}

For each goal below, write a 2-3 sentence progress narrative that:
1. States the current performance level with specific data
2. Describes the trend (progressing/maintaining/regressing)
3. Notes whether the student is on track for the annual goal
4. Uses parent-friendly language (avoid jargon)
5. Ends with a brief note about what comes next

GOALS AND DATA:
"""

    for i, goal in enumerate(goals_with_data, 1):
        prompt += f"""
--- GOAL {i} ---
Goal Area: {goal.get('goal_area', 'N/A')}
Goal Text: {goal.get('goal_text', 'N/A')}
Measurement Method: {goal.get('method', 'N/A')}
Baseline (starting level): {goal.get('baseline', 'N/A')}
Annual Target: {goal.get('target', 'N/A')}
Current Level: {goal.get('current_level', 'N/A')}
Trend: {goal.get('trend', 'N/A')}
Data Points This Period: {goal.get('data_points_this_period', 0)}
On Track for Annual Goal: {'Yes' if goal.get('on_track_for_annual') else 'No' if goal.get('on_track_for_annual') is False else 'Unable to determine'}
Mastery Status: {'MASTERED' if goal.get('mastery_status', {}).get('mastered') else 'In Progress'}
"""

    prompt += """
FORMAT YOUR RESPONSE AS:

**[Goal Area]: [Brief Goal Description]**
[2-3 sentence narrative]
Status: [Progressing/Maintaining/Regressing] | On Track: [Yes/No]

---

Remember:
- Be honest about regression but frame it constructively
- Suggest parent involvement where appropriate
- Note any mastered goals enthusiastically
- Keep language at 8th grade reading level for parent accessibility
- Use the student's first name
"""

    return prompt


def generate_report_for_printing(report):
    """
    Format a progress report for print output.

    Args:
        report (dict): Output from generate_progress_report()

    Returns:
        dict: Print-formatted report data
    """
    student = report.get('student_info', {})

    header = {
        'title': 'IEP Progress Report',
        'student_name': student.get('name', 'Unknown'),
        'student_id': report.get('student_id', ''),
        'grade': student.get('grade', ''),
        'teacher': student.get('teacher', ''),
        'case_manager': student.get('case_manager', ''),
        'reporting_period': report.get('period_name', ''),
        'date_range': report.get('date_range', {}),
        'generated_date': report.get('generated_date', ''),
        'school': student.get('school', ''),
        'district': student.get('district', 'Kentucky')
    }

    goals_formatted = []
    for goal in report.get('goals', []):
        goals_formatted.append({
            'area': goal.get('goal_area', ''),
            'text': goal.get('goal_text', ''),
            'baseline': goal.get('baseline', ''),
            'current': goal.get('current_level', ''),
            'target': goal.get('target', ''),
            'trend': goal.get('trend_label', ''),
            'on_track': '✓ Yes' if goal.get('on_track_for_annual') else '✗ No',
            'data_points': goal.get('data_points_this_period', 0),
            'narrative': goal.get('narrative', '[Narrative to be added]')
        })

    return {
        'header': header,
        'goals': goals_formatted,
        'summary': report.get('summary', {}),
        'compliance': report.get('kentucky_compliance', {}),
        'signatures': {
            'teacher': '',
            'parent': '',
            'date_sent': '',
            'date_returned': ''
        }
    }


def get_available_periods(student_id):
    """
    Determine which reporting periods have data available.

    Args:
        student_id (str): Student identifier

    Returns:
        list: Available reporting periods with date ranges
    """
    summary = get_student_data_summary(student_id)
    if not summary or summary['total_data_points'] == 0:
        return []

    first_date = None
    last_date = None

    for goal_id, goal_info in summary.get('goals', {}).items():
        if goal_info.get('first_date'):
            if first_date is None or goal_info['first_date'] < first_date:
                first_date = goal_info['first_date']
        if goal_info.get('last_date'):
            if last_date is None or goal_info['last_date'] > last_date:
                last_date = goal_info['last_date']

    if not first_date:
        return []

    # Determine school year
    first_dt = datetime.strptime(first_date, '%Y-%m-%d')
    if first_dt.month >= 8:
        school_year_start = first_dt.year
    else:
        school_year_start = first_dt.year - 1

    available = []
    for period_key, period_info in REPORTING_PERIODS.items():
        try:
            start, end = _get_reporting_dates(
                period_key,
                f"{school_year_start}-{school_year_start + 1}"
            )
            # Check if any data falls in this range
            if start <= last_date and end >= first_date:
                available.append({
                    'period': period_key,
                    'name': period_info['name'],
                    'start': start,
                    'end': end
                })
        except Exception:
            continue

    return available
