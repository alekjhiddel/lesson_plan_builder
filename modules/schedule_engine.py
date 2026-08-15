"""
Schedule Engine Module
Solves the aide-assignment scheduling problem using constraint satisfaction.
Considers: homeroom times, aide escorts, partner teacher, minimum room coverage,
center rotations, and 1:1 time maximization.
"""

import json
import os
from datetime import datetime, timedelta
from itertools import combinations

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SCHEDULE_CONFIG_FILE = os.path.join(DATA_DIR, 'schedule_config.json')


def get_schedule_config():
    """Load schedule configuration."""
    if os.path.exists(SCHEDULE_CONFIG_FILE):
        with open(SCHEDULE_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return get_default_config()


def get_default_config():
    """Default scheduling configuration."""
    return {
        'num_dedicated_aides': 2,
        'has_floater': True,
        'floater_name': 'Floater',
        'aide_names': ['Aide 1', 'Aide 2'],
        'partner_teacher': {
            'enabled': False,
            'name': '',
            'num_aides': 2,
            'aide_names': ['Partner Aide 1', 'Partner Aide 2'],
            'num_students': 0,
            'shared_floater': False,  # Does the floater cover both rooms?
            'notes': ''
        },
        'time_blocks': [
            {'name': 'Arrival / Morning Routine', 'start': '8:00', 'end': '8:20', 'type': 'routine'},
            {'name': 'Morning Meeting', 'start': '8:20', 'end': '8:40', 'type': 'whole_group'},
            {'name': 'Centers Block 1', 'start': '8:40', 'end': '9:40', 'type': 'centers'},
            {'name': 'Snack / Life Skills', 'start': '9:40', 'end': '10:00', 'type': 'routine'},
            {'name': 'Specials / Recess', 'start': '10:00', 'end': '10:30', 'type': 'specials'},
            {'name': '1:1 Aide Time Block 1', 'start': '10:30', 'end': '11:15', 'type': 'individual'},
            {'name': 'Lunch', 'start': '11:15', 'end': '11:45', 'type': 'routine'},
            {'name': 'Rest / Sensory', 'start': '11:45', 'end': '12:05', 'type': 'sensory'},
            {'name': 'Centers Block 2', 'start': '12:05', 'end': '1:05', 'type': 'centers'},
            {'name': 'Story / Group', 'start': '1:05', 'end': '1:25', 'type': 'whole_group'},
            {'name': '1:1 Aide Time Block 2', 'start': '1:25', 'end': '2:05', 'type': 'individual'},
            {'name': 'Closing / Dismissal', 'start': '2:05', 'end': '2:35', 'type': 'routine'},
        ],
        'min_aides_in_own_room': 1,    # At least 1 aide must stay in YOUR room at all times
        'min_aides_in_partner_room': 1, # At least 1 aide must stay in PARTNER room at all times (if partner enabled)
        'center_rotation_minutes': 20,
        'center_groups': 3,
    }


def save_schedule_config(config):
    """Save schedule configuration."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SCHEDULE_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def generate_schedule(students, config):
    """
    Generate an optimized daily schedule that:
    1. Respects each student's homeroom time
    2. Ensures minimum staff coverage in the room at all times
    3. Assigns aides to homeroom escorts when needed
    4. Maximizes 1:1 instructional time
    5. Balances aide workload
    6. Coordinates with partner teacher if applicable
    
    Returns a schedule dict with time blocks and assignments.
    """
    schedule_config = get_schedule_config()
    
    # Gather all staff
    staff = _build_staff_list(schedule_config)
    
    # Gather all student homeroom commitments
    homeroom_events = _build_homeroom_events(students)
    
    # For each time block, determine who's available and assign
    daily_schedule = []
    
    for block in schedule_config['time_blocks']:
        block_schedule = _schedule_block(
            block=block,
            students=students,
            staff=staff,
            homeroom_events=homeroom_events,
            config=schedule_config
        )
        daily_schedule.append(block_schedule)
    
    # Generate the aide assignment grid
    aide_grid = _build_aide_grid(daily_schedule, staff)
    
    # Generate the student location grid
    student_grid = _build_student_grid(daily_schedule, students)
    
    # Generate warnings/conflicts
    warnings = _check_conflicts(daily_schedule, schedule_config)
    
    return {
        'daily_schedule': daily_schedule,
        'aide_grid': aide_grid,
        'student_grid': student_grid,
        'warnings': warnings,
        'staff': staff,
        'generated_at': datetime.now().isoformat()
    }


def _build_staff_list(config):
    """Build complete list of available staff."""
    staff = []
    
    # Dedicated aides
    for i, name in enumerate(config.get('aide_names', ['Aide 1', 'Aide 2'])):
        staff.append({
            'id': f'aide_{i+1}',
            'name': name,
            'role': 'dedicated_aide',
            'room': 'primary'
        })
    
    # Floater
    if config.get('has_floater'):
        staff.append({
            'id': 'floater',
            'name': config.get('floater_name', 'Floater'),
            'role': 'floater',
            'room': 'flex'  # Can be in either room
        })
    
    # Partner teacher aides
    partner = config.get('partner_teacher', {})
    if partner.get('enabled'):
        for i, name in enumerate(partner.get('aide_names', [])):
            staff.append({
                'id': f'partner_aide_{i+1}',
                'name': name,
                'role': 'partner_aide',
                'room': 'partner'
            })
    
    return staff


def _build_homeroom_events(students):
    """Extract homeroom schedules from student profiles."""
    events = []
    for student in students:
        if student.get('homeroom_attends'):
            events.append({
                'student_id': student['id'],
                'student_name': student['name'],
                'duration': student.get('homeroom_duration', ''),
                'schedule': student.get('homeroom_schedule', ''),
                'needs_aide': student.get('homeroom_aide_accompanies', False)
            })
    return events


def _schedule_block(block, students, staff, homeroom_events, config):
    """Schedule a single time block."""
    block_name = block['name']
    block_type = block['type']
    
    # Determine which students are OUT (at homeroom) during this block
    students_out = []
    aides_escorting = []
    
    for event in homeroom_events:
        # Simple heuristic: check if this block overlaps with homeroom schedule
        # In v2, we'll parse actual times. For now, use a smarter matching.
        if _block_overlaps_homeroom(block, event):
            students_out.append(event['student_name'])
            if event['needs_aide']:
                # Assign floater first, then a dedicated aide
                escort_aide = _pick_escort_aide(staff, aides_escorting, config)
                if escort_aide:
                    aides_escorting.append(escort_aide)
    
    # Students IN the room
    students_in = [s for s in students if s['name'] not in students_out]
    
    # Available staff (not escorting)
    escorting_ids = [a['id'] for a in aides_escorting]
    available_staff = [s for s in staff if s['id'] not in escorting_ids and s['room'] != 'partner']
    
    # Build assignments based on block type
    assignments = []
    
    if block_type == 'centers':
        assignments = _assign_centers(students_in, available_staff, config)
    elif block_type == 'individual':
        assignments = _assign_individual(students_in, available_staff)
    elif block_type == 'whole_group':
        assignments = [{'type': 'whole_group', 'staff': available_staff, 'students': students_in}]
    else:
        assignments = [{'type': block_type, 'staff': available_staff, 'students': students_in}]
    
    return {
        'block': block,
        'students_in_room': [s['name'] for s in students_in],
        'students_at_homeroom': students_out,
        'aides_escorting': [{'aide': a['name'], 'escorting': 'student to homeroom'} for a in aides_escorting],
        'available_staff': [s['name'] for s in available_staff],
        'assignments': assignments
    }


def _block_overlaps_homeroom(block, homeroom_event):
    """
    Determine if a time block overlaps with a student's homeroom time.
    Uses simple keyword/time matching.
    """
    schedule_text = homeroom_event.get('schedule', '').lower()
    block_start = block.get('start', '')
    
    # Parse block start time for comparison
    try:
        block_hour = int(block_start.split(':')[0])
        block_min = int(block_start.split(':')[1])
    except:
        return False
    
    # Check common patterns in homeroom_schedule
    if 'morning' in schedule_text or 'am' in schedule_text:
        # Morning homeroom = overlaps with blocks between 8:30-10:30
        if 8 <= block_hour <= 10:
            return True
    elif 'afternoon' in schedule_text or 'pm' in schedule_text:
        # Afternoon homeroom = overlaps with blocks after 12:00
        if block_hour >= 12:
            return True
    elif ':' in schedule_text:
        # Try to parse specific time like "9:00-9:30"
        try:
            parts = schedule_text.replace(' ', '').split('-')
            if len(parts) == 2:
                start_parts = parts[0].split(':')
                end_parts = parts[1].split(':')
                hr_start = int(start_parts[0])
                hr_end = int(end_parts[0])
                if hr_start <= block_hour < hr_end:
                    return True
        except:
            pass
    
    return False


def _pick_escort_aide(staff, already_escorting, config):
    """Pick which aide escorts to homeroom. Prefer floater."""
    """Respects constraint: at least 1 aide must remain in EACH room."""
    escorting_ids = [a['id'] for a in already_escorting]
    
    # Try floater first
    for s in staff:
        if s['role'] == 'floater' and s['id'] not in escorting_ids:
            return s
    
    # Then try dedicated aides — but only if pulling one still leaves ≥1 in the room
    dedicated_available = [s for s in staff 
                          if s['role'] == 'dedicated_aide' and s['id'] not in escorting_ids]
    if len(dedicated_available) > config.get('min_aides_in_own_room', 1):
        return dedicated_available[0]
    
    # If partner enabled with shared floater, check partner aides
    partner = config.get('partner_teacher', {})
    if partner.get('enabled'):
        partner_available = [s for s in staff
                           if s['role'] == 'partner_aide' and s['id'] not in escorting_ids]
        min_partner = config.get('min_aides_in_partner_room', 1)
        if len(partner_available) > min_partner:
            return partner_available[0]
    
    # Cannot escort without violating coverage — return None (student can't go this block)
    return None


def _pick_escort_aide_ORIGINAL(staff, already_escorting, config):
    """DEPRECATED — kept for reference."""
    escorting_ids = [a['id'] for a in already_escorting]
    for s in staff:
        if s['role'] == 'floater' and s['id'] not in escorting_ids:
            return s
    for s in staff:
        if s['role'] == 'dedicated_aide' and s['id'] not in escorting_ids and s['room'] == 'primary':
            return s
    return None


def _assign_centers(students_in, available_staff, config):
    """Assign students to center groups with staff."""
    num_groups = min(config.get('center_groups', 3), len(available_staff))
    
    if not students_in or not available_staff:
        return []
    
    # Split students into groups
    groups = [[] for _ in range(num_groups)]
    for i, student in enumerate(students_in):
        groups[i % num_groups].append(student['name'] if isinstance(student, dict) else student)
    
    # Assign staff to groups
    assignments = []
    for i, group in enumerate(groups):
        staff_member = available_staff[i] if i < len(available_staff) else available_staff[-1]
        assignments.append({
            'type': 'center',
            'group_number': i + 1,
            'staff': staff_member['name'],
            'students': group,
            'center_name': f'Center {i + 1}'
        })
    
    return assignments


def _assign_individual(students_in, available_staff):
    """Assign 1:1 aide time — pair each aide with students in rotation."""
    if not students_in or not available_staff:
        return []
    
    assignments = []
    for i, staff_member in enumerate(available_staff):
        # Each aide gets a portion of the students
        aide_students = []
        for j, student in enumerate(students_in):
            if j % len(available_staff) == i:
                name = student['name'] if isinstance(student, dict) else student
                aide_students.append(name)
        
        if aide_students:
            assignments.append({
                'type': 'individual',
                'staff': staff_member['name'],
                'students': aide_students,
                'note': f'{len(aide_students)} students, rotating'
            })
    
    return assignments


def _build_aide_grid(daily_schedule, staff):
    """Build a staff assignment grid (who is where each block)."""
    grid = {}
    for s in staff:
        grid[s['name']] = []
    
    for block_schedule in daily_schedule:
        block_name = block_schedule['block']['name']
        
        # Track who's doing what
        for s in staff:
            assignment = 'Available'
            
            # Check if escorting
            for escort in block_schedule.get('aides_escorting', []):
                if escort['aide'] == s['name']:
                    assignment = '→ Homeroom escort'
                    break
            
            # Check center/individual assignments
            if assignment == 'Available':
                for a in block_schedule.get('assignments', []):
                    if isinstance(a.get('staff'), str) and a['staff'] == s['name']:
                        if a['type'] == 'center':
                            assignment = f"Center {a.get('group_number', '?')}: {', '.join(a.get('students', [])[:3])}"
                        elif a['type'] == 'individual':
                            assignment = f"1:1 with: {', '.join(a.get('students', [])[:2])}"
                        else:
                            assignment = f"In room ({a['type']})"
                        break
            
            if s['name'] in grid:
                grid[s['name']].append({
                    'block': block_name,
                    'assignment': assignment
                })
    
    return grid


def _build_student_grid(daily_schedule, students):
    """Build a student location grid (where each student is each block)."""
    grid = {}
    for s in students:
        grid[s['name']] = []
    
    for block_schedule in daily_schedule:
        block_name = block_schedule['block']['name']
        
        for s in students:
            if s['name'] in block_schedule.get('students_at_homeroom', []):
                location = '→ Homeroom'
            else:
                location = 'In classroom'
                # Check specific assignment
                for a in block_schedule.get('assignments', []):
                    students_list = a.get('students', [])
                    if s['name'] in students_list:
                        if a['type'] == 'center':
                            location = f"Center {a.get('group_number', '?')}"
                        elif a['type'] == 'individual':
                            location = f"1:1 with {a.get('staff', 'aide')}"
                        break
            
            if s['name'] in grid:
                grid[s['name']].append({
                    'block': block_name,
                    'location': location
                })
    
    return grid


def _check_conflicts(daily_schedule, config):
    """Check for scheduling conflicts and generate warnings."""
    warnings = []
    min_aides_own = config.get('min_aides_in_own_room', 1)
    partner_enabled = config.get('partner_teacher', {}).get('enabled', False)
    min_aides_partner = config.get('min_aides_in_partner_room', 1) if partner_enabled else 0
    
    for block_schedule in daily_schedule:
        # Count aides staying in the primary room (not escorting, not partner-room aides)
        available_own = [s for s in block_schedule.get('available_staff', [])
                        if s not in [a['aide'] for a in block_schedule.get('aides_escorting', [])]]
        own_aide_count = len(available_own)
        
        if own_aide_count < min_aides_own:
            warnings.append({
                'severity': 'critical',
                'block': block_schedule['block']['name'],
                'message': f"Only {own_aide_count} aide(s) in YOUR room (need at least {min_aides_own}). "
                          f"{len(block_schedule.get('aides_escorting', []))} aide(s) escorting to homeroom."
            })
        
        # Check partner room coverage (if applicable)
        if partner_enabled and block_schedule.get('aides_escorting'):
            # If a partner aide is escorting, check partner room coverage
            partner_escorting = [a for a in block_schedule.get('aides_escorting', [])
                                if 'partner' in a.get('aide', '').lower()]
            partner_total = config.get('partner_teacher', {}).get('num_aides', 2)
            partner_remaining = partner_total - len(partner_escorting)
            if partner_remaining < min_aides_partner:
                warnings.append({
                    'severity': 'critical',
                    'block': block_schedule['block']['name'],
                    'message': f"Partner room has only {partner_remaining} aide(s) (need {min_aides_partner}). "
                              f"Cannot pull partner aide for escort."
                })
        
        # Check if too many students for available staff
        students_in_count = len(block_schedule.get('students_in_room', []))
        total_in_room = own_aide_count + 1  # +1 for teacher
        if students_in_count > 0 and total_in_room > 0:
            ratio = students_in_count / total_in_room
            if ratio > 4:
                warnings.append({
                    'severity': 'warning',
                    'block': block_schedule['block']['name'],
                    'message': f"High student:staff ratio ({students_in_count}:{total_in_room} = {ratio:.1f}:1)"
                })
    
    return warnings


def format_schedule_for_display(schedule):
    """Format the generated schedule as readable HTML/text."""
    output = []
    output.append("<h2>📅 Daily Schedule</h2>")
    
    # Warnings first
    if schedule.get('warnings'):
        output.append("<div class=\'alert alert-error\'>")
        output.append("<strong>⚠️ Scheduling Conflicts:</strong><ul>")
        for w in schedule['warnings']:
            output.append(f"<li><strong>{w['block']}:</strong> {w['message']}</li>")
        output.append("</ul></div>")
    
    # Main schedule
    output.append("<table class=\'schedule-table\'>")
    output.append("<tr><th>Time Block</th><th>Students in Room</th><th>At Homeroom</th><th>Staff Available</th></tr>")
    
    for block in schedule['daily_schedule']:
        b = block['block']
        in_room = len(block.get('students_in_room', []))
        at_hr = len(block.get('students_at_homeroom', []))
        staff = len(block.get('available_staff', []))
        escorts = block.get('aides_escorting', [])
        
        escort_note = f" ({len(escorts)} escorting)" if escorts else ""
        
        output.append(f"<tr><td><strong>{b['name']}</strong><br><small>{b['start']}-{b['end']}</small></td>")
        output.append(f"<td>{in_room} students</td>")
        output.append(f"<td>{at_hr} at homeroom</td>")
        output.append(f"<td>{staff} aides + teacher{escort_note}</td></tr>")
    
    output.append("</table>")
    
    # Aide grid
    output.append("<h2>👥 Staff Assignment Grid</h2>")
    output.append("<table class=\'schedule-table\'>")
    
    # Header
    output.append("<tr><th>Time Block</th>")
    for name in schedule.get('aide_grid', {}).keys():
        output.append(f"<th>{name}</th>")
    output.append("</tr>")
    
    # Rows
    if schedule.get('aide_grid'):
        first_aide = list(schedule['aide_grid'].values())[0]
        for i, entry in enumerate(first_aide):
            output.append(f"<tr><td><strong>{entry['block']}</strong></td>")
            for aide_name, blocks in schedule['aide_grid'].items():
                if i < len(blocks):
                    output.append(f"<td>{blocks[i]['assignment']}</td>")
            output.append("</tr>")
    
    output.append("</table>")
    
    return "\n".join(output)


def format_schedule_for_prompt(schedule, students):
    """Format schedule as text for inclusion in ChatGPT prompts."""
    lines = []
    lines.append("GENERATED DAILY SCHEDULE:")
    lines.append("")
    
    for block in schedule['daily_schedule']:
        b = block['block']
        lines.append(f"--- {b['start']}-{b['end']}: {b['name']} ---")
        lines.append(f"  Students in room: {len(block.get('students_in_room', []))}")
        
        if block.get('students_at_homeroom'):
            lines.append(f"  At homeroom: {', '.join(block['students_at_homeroom'])}")
        
        if block.get('aides_escorting'):
            for e in block['aides_escorting']:
                lines.append(f"  {e['aide']} → escorting to homeroom")
        
        lines.append(f"  Available staff: {', '.join(block.get('available_staff', []))}")
        
        if block.get('assignments'):
            for a in block['assignments']:
                if a['type'] == 'center':
                    lines.append(f"  Center {a.get('group_number')}: {a.get('staff')} with {', '.join(a.get('students', []))}")
                elif a['type'] == 'individual':
                    lines.append(f"  1:1: {a.get('staff')} → {', '.join(a.get('students', []))}")
        lines.append("")
    
    if schedule.get('warnings'):
        lines.append("⚠️ CONFLICTS TO RESOLVE:")
        for w in schedule['warnings']:
            lines.append(f"  [{w['severity'].upper()}] {w['block']}: {w['message']}")
    
    return "\n".join(lines)
