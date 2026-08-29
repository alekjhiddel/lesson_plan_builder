"""
Group Manager Module
Handles ability-based and goal-based student grouping.
Supports auto-grouping by ability scores, manual overrides,
and mid-year moves for IEP goal changes.

Groups are stored in data/groups.json.
Two group types: "ability" (stable, set at start of year) and
"goal" (shift when individual IEPs renew).
"""

import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
GROUPS_FILE = os.path.join(DATA_DIR, 'groups.json')

# Ability dimension scoring maps (lower = more support needed)
FUNCTIONAL_LEVELS = {
    'pre-emerging': 0,
    'emerging': 1,
    'developing': 2,
    'functional': 3
}

COMMUNICATION_TIERS = {
    'pre-verbal': 0,
    'single-words': 1,
    'phrases': 2,
    'sentences': 3
}

INDEPENDENCE_TIERS = {
    'full-physical': 0,
    'partial-physical': 1,
    'gestural': 2,
    'verbal': 3,
    'independent': 4
}

ACADEMIC_ACCESS = {
    'sensory': 0,
    'concrete': 1,
    'pictorial': 2,
    'symbolic': 3
}

# Weights for composite score (from spec)
WEIGHTS = {
    'functional_level': 3,
    'communication_tier': 2,
    'independence_tier': 2,
    'academic_access': 1
}

# Default group names (colors — Ashley's preference)
DEFAULT_GROUP_NAMES = ['Red', 'Blue', 'Green']
DEFAULT_GROUP_COLORS = ['#F44336', '#2196F3', '#4CAF50']

# Instruction level descriptions based on group average score
INSTRUCTION_LEVELS = [
    (0, 5, 'Highest support — activities should be sensory/tactile with hand-over-hand support. Focus on cause-and-effect, requesting, and single-step routines.'),
    (5, 10, 'Moderate support — picture-schedule activities with verbal/gestural prompts. Focus on 2-step routines, choice-making, and functional communication.'),
    (10, 15, 'Developing independence — visual task analysis with fading prompts. Focus on multi-step routines, social interaction, and functional academics.'),
    (15, 999, 'Most independent — structured activities with verbal prompts only. Focus on independence, problem-solving, and community readiness skills.')
]


def _ensure_groups_file():
    """Create groups.json if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'w') as f:
            json.dump({'groups': []}, f, indent=2)


def _load_groups():
    """Load all groups from disk."""
    _ensure_groups_file()
    try:
        with open(GROUPS_FILE, 'r') as f:
            data = json.load(f)
        return data.get('groups', [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_groups(groups):
    """Save all groups to disk."""
    _ensure_groups_file()
    with open(GROUPS_FILE, 'w') as f:
        json.dump({'groups': groups}, f, indent=2)


# ============================================================
# PUBLIC API
# ============================================================

def get_all_groups():
    """Get all groups."""
    return _load_groups()


def get_groups_by_type(group_type):
    """Get groups filtered by type ('ability' or 'goal')."""
    return [g for g in _load_groups() if g.get('group_type') == group_type]


def get_group(group_id):
    """Get a single group by ID."""
    for group in _load_groups():
        if group['id'] == group_id:
            return group
    return None


def create_group(name, group_type='ability', color='#9E9E9E', 
                 student_ids=None, description='', goal_tags=None):
    """Create a new group."""
    groups = _load_groups()
    
    group = {
        'id': str(uuid.uuid4()),
        'name': name,
        'group_type': group_type,
        'color': color,
        'student_ids': student_ids or [],
        'description': description,
        'goal_tags': goal_tags or [],
        'auto_generated': False,
        'last_updated': datetime.now().isoformat()
    }
    
    groups.append(group)
    _save_groups(groups)
    return group


def update_group(group_id, **kwargs):
    """Update group fields. Pass any field as a keyword argument."""
    groups = _load_groups()
    for i, group in enumerate(groups):
        if group['id'] == group_id:
            for key, value in kwargs.items():
                if key != 'id':
                    group[key] = value
            group['last_updated'] = datetime.now().isoformat()
            groups[i] = group
            _save_groups(groups)
            return group
    return None


def delete_group(group_id):
    """Delete a group."""
    groups = _load_groups()
    groups = [g for g in groups if g['id'] != group_id]
    _save_groups(groups)
    return True


def add_student_to_group(group_id, student_id):
    """Add a student to a group."""
    groups = _load_groups()
    for i, group in enumerate(groups):
        if group['id'] == group_id:
            if student_id not in group['student_ids']:
                group['student_ids'].append(student_id)
                group['last_updated'] = datetime.now().isoformat()
                groups[i] = group
                _save_groups(groups)
            return group
    return None


def remove_student_from_group(group_id, student_id):
    """Remove a student from a group."""
    groups = _load_groups()
    for i, group in enumerate(groups):
        if group['id'] == group_id:
            if student_id in group['student_ids']:
                group['student_ids'].remove(student_id)
                group['last_updated'] = datetime.now().isoformat()
                groups[i] = group
                _save_groups(groups)
            return group
    return None


def move_student_between_groups(student_id, from_group_id, to_group_id):
    """Move a student from one group to another."""
    remove_student_from_group(from_group_id, student_id)
    return add_student_to_group(to_group_id, student_id)


def get_student_groups(student_id):
    """Get all groups a student belongs to."""
    return [g for g in _load_groups() if student_id in g.get('student_ids', [])]


def get_ungrouped_students(all_students, group_type='ability'):
    """Get students not in any group of the given type."""
    groups = get_groups_by_type(group_type)
    grouped_ids = set()
    for group in groups:
        grouped_ids.update(group.get('student_ids', []))
    
    return [s for s in all_students if s['id'] not in grouped_ids]


# ============================================================
# AUTO-GROUPING ALGORITHM
# ============================================================

def calculate_ability_score(student):
    """
    Calculate composite ability score for a student.
    Score = functional(×3) + communication(×2) + independence(×2) + academic(×1)
    Range: 0 (highest support) to 28 (most independent)
    """
    ability = student.get('ability_level', {})
    
    func_score = FUNCTIONAL_LEVELS.get(ability.get('functional_level', ''), 0)
    comm_score = COMMUNICATION_TIERS.get(ability.get('communication_tier', ''), 0)
    indep_score = INDEPENDENCE_TIERS.get(ability.get('independence_tier', ''), 0)
    acad_score = ACADEMIC_ACCESS.get(ability.get('academic_access', ''), 0)
    
    return (func_score * WEIGHTS['functional_level'] +
            comm_score * WEIGHTS['communication_tier'] +
            indep_score * WEIGHTS['independence_tier'] +
            acad_score * WEIGHTS['academic_access'])


def get_instruction_level(avg_score):
    """Get the instruction level description for a group's average score."""
    for low, high, description in INSTRUCTION_LEVELS:
        if low <= avg_score < high:
            return description
    return INSTRUCTION_LEVELS[-1][2]


def auto_group_by_ability(students):
    """
    Auto-group students into 2-3 ability groups.
    
    Algorithm:
    1. Score each student on the composite scale
    2. Sort by score
    3. Divide into 2-3 clusters where max spread within a group is 2 points
    4. Name groups with default colors (Red, Blue, Green)
    
    Returns list of group dicts (not yet saved — caller decides to accept or adjust).
    """
    if len(students) < 2:
        return []
    
    # Score each student
    scored = []
    for student in students:
        score = calculate_ability_score(student)
        scored.append((student, score))
    
    # Sort by score (lowest = highest support)
    scored.sort(key=lambda x: x[1])
    
    # Cluster using a greedy approach with max spread of 2
    clusters = []
    current_cluster = [scored[0]]
    
    for student, score in scored[1:]:
        cluster_min = current_cluster[0][1]
        if score - cluster_min <= 2:
            current_cluster.append((student, score))
        else:
            clusters.append(current_cluster)
            current_cluster = [(student, score)]
    clusters.append(current_cluster)
    
    # Enforce max 3 groups — merge smallest adjacent clusters if needed
    while len(clusters) > 3:
        # Find the two adjacent clusters with smallest combined size
        min_size = float('inf')
        merge_idx = 0
        for i in range(len(clusters) - 1):
            combined = len(clusters[i]) + len(clusters[i + 1])
            if combined < min_size:
                min_size = combined
                merge_idx = i
        clusters[merge_idx] = clusters[merge_idx] + clusters[merge_idx + 1]
        del clusters[merge_idx + 1]
    
    # If we got just 1 cluster and have enough students, try splitting at median
    if len(clusters) == 1 and len(clusters[0]) >= 4:
        mid = len(clusters[0]) // 2
        clusters = [clusters[0][:mid], clusters[0][mid:]]
    
    # Build group objects
    groups = []
    for i, cluster in enumerate(clusters):
        name = DEFAULT_GROUP_NAMES[i] if i < len(DEFAULT_GROUP_NAMES) else f'Group {i + 1}'
        color = DEFAULT_GROUP_COLORS[i] if i < len(DEFAULT_GROUP_COLORS) else '#9E9E9E'
        
        student_ids = [s[0]['id'] for s in cluster]
        scores = [s[1] for s in cluster]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Build description from the students' ability levels
        func_levels = set()
        comm_levels = set()
        for s, _ in cluster:
            ability = s.get('ability_level', {})
            func_levels.add(ability.get('functional_level', 'unknown'))
            comm_levels.add(ability.get('communication_tier', 'unknown'))
        
        description = (
            f"{', '.join(sorted(func_levels))} functional level, "
            f"{', '.join(sorted(comm_levels))} communication"
        )
        
        group = {
            'id': str(uuid.uuid4()),
            'name': name,
            'group_type': 'ability',
            'color': color,
            'student_ids': student_ids,
            'description': description,
            'goal_tags': [],
            'auto_generated': True,
            'instruction_level': get_instruction_level(avg_score),
            'avg_score': round(avg_score, 1),
            'last_updated': datetime.now().isoformat()
        }
        groups.append(group)
    
    return groups


def accept_auto_groups(groups):
    """
    Accept auto-generated groups: clear existing ability groups and save new ones.
    Goal groups are preserved.
    """
    existing = _load_groups()
    # Keep goal groups, replace ability groups
    goal_groups = [g for g in existing if g.get('group_type') == 'goal']
    _save_groups(goal_groups + groups)
    return goal_groups + groups


def suggest_goal_group_changes(student):
    """
    Check if a student's IEP goals still match their current goal groups.
    Returns list of suggestions if there's a mismatch.
    """
    student_id = student['id']
    goal_groups = get_groups_by_type('goal')
    student_goal_groups = [g for g in goal_groups if student_id in g.get('student_ids', [])]
    
    if not student_goal_groups:
        return []
    
    suggestions = []
    student_goals = ' '.join(student.get('iep_goals', [])).lower()
    
    for group in student_goal_groups:
        goal_tags = group.get('goal_tags', [])
        if goal_tags:
            matches = sum(1 for tag in goal_tags if tag.lower() in student_goals)
            if matches == 0:
                suggestions.append({
                    'type': 'mismatch',
                    'group_id': group['id'],
                    'group_name': group['name'],
                    'message': (
                        f"{student['name']}'s current IEP goals may no longer match "
                        f"the '{group['name']}' goal group (tags: {', '.join(goal_tags)}). "
                        f"Consider moving them to a different goal group."
                    )
                })
    
    return suggestions


# ============================================================
# YEAR LIFECYCLE INTEGRATION
# ============================================================

def reset_all_groups():
    """
    Clear all groups for a new school year.
    Called by the year lifecycle system during annual rollover.
    """
    _save_groups([])
    return True


def get_group_summary():
    """Get a quick summary of current groups for the dashboard."""
    groups = _load_groups()
    ability_groups = [g for g in groups if g.get('group_type') == 'ability']
    goal_groups = [g for g in groups if g.get('group_type') == 'goal']
    
    total_students = set()
    for g in groups:
        total_students.update(g.get('student_ids', []))
    
    return {
        'total_groups': len(groups),
        'ability_groups': len(ability_groups),
        'goal_groups': len(goal_groups),
        'students_grouped': len(total_students),
        'groups': groups
    }
