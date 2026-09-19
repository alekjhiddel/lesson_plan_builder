"""
Center Manager Module
Manages the fixed four-center rotation model for the MSD classroom.

The four centers are FIXED and set in stone — they cannot be added,
removed, renamed, or reordered. Only the rotation length (in minutes)
is customizable.

Config is stored in data/centers_config.json with the shape:
    {"centers": [...4 fixed centers...], "rotation_minutes": 10}

Rotation length is clamped to the inclusive range 5..30 minutes.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CENTERS_FILE = os.path.join(DATA_DIR, 'centers_config.json')

# The four FIXED centers — set in stone. Always forced back to these
# canonical definitions on every ensure/self-heal. No add/remove/rename API.
FIXED_CENTERS = [
    {'id': 'reading', 'name': 'Reading Center', 'type': 'reading', 'order': 1},
    {'id': 'math', 'name': 'Math Center', 'type': 'math', 'order': 2},
    {'id': 'motor', 'name': 'Motor Center', 'type': 'fine_motor', 'order': 3},
    {'id': 'sel', 'name': 'Social/Emotional/Adaptive/Life Skills Center',
     'type': 'sel_adaptive_life', 'order': 4},
]

# Rotation length bounds (inclusive) and default.
MIN_ROTATION_MINUTES = 5
MAX_ROTATION_MINUTES = 30
DEFAULT_ROTATION_MINUTES = 10


def _canonical_centers():
    """Return a fresh deep copy of the 4 fixed centers, ordered by 'order'."""
    centers = [dict(c) for c in FIXED_CENTERS]
    centers.sort(key=lambda c: c['order'])
    return centers


def _coerce_rotation_minutes(value):
    """
    Coerce/validate a rotation-minutes value.

    Accepts a real int (bool is rejected), or a numeric string / float that
    represents a whole number, then clamps it to [MIN, MAX]. Returns a valid
    int on success, or None if the value cannot be interpreted as a whole
    number (junk, None, NaN/inf, non-numeric string, fractional value, bool).
    """
    # Reject bool explicitly (bool is a subclass of int).
    if isinstance(value, bool):
        return None
    # Plain int is the happy path.
    if isinstance(value, int):
        n = value
    elif isinstance(value, float):
        # Reject NaN/inf and non-whole floats.
        if value != value or value in (float('inf'), float('-inf')):
            return None
        if not value.is_integer():
            return None
        n = int(value)
    elif isinstance(value, str):
        s = value.strip()
        try:
            n = int(s)
        except (ValueError, TypeError):
            return None
    else:
        return None
    # Clamp to the inclusive range.
    if n < MIN_ROTATION_MINUTES:
        n = MIN_ROTATION_MINUTES
    elif n > MAX_ROTATION_MINUTES:
        n = MAX_ROTATION_MINUTES
    return n


def _ensure_config():
    """
    Ensure data/centers_config.json exists and is valid. Idempotent.

    - Creates the file with defaults if missing.
    - If the file is corrupt/invalid JSON or missing keys, SELF-HEALS:
      the 4 fixed centers are always forced back to canonical, and a valid
      existing rotation_minutes is preserved (never clobbered); otherwise
      the default (10) is used.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    rotation = DEFAULT_ROTATION_MINUTES
    needs_write = False

    if not os.path.exists(CENTERS_FILE):
        needs_write = True
    else:
        try:
            with open(CENTERS_FILE, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError, OSError):
            data = None
            needs_write = True

        if isinstance(data, dict):
            # Preserve a valid existing rotation_minutes; heal anything else.
            healed_rotation = _coerce_rotation_minutes(data.get('rotation_minutes'))
            if healed_rotation is None:
                rotation = DEFAULT_ROTATION_MINUTES
                needs_write = True
            else:
                rotation = healed_rotation
                # If the stored value differed from the healed/clamped one,
                # rewrite so the file reflects the canonical stored value.
                if data.get('rotation_minutes') != healed_rotation:
                    needs_write = True
            # Centers are set in stone — rewrite if they don't match canonical.
            if data.get('centers') != _canonical_centers():
                needs_write = True
        else:
            # Not a dict (e.g. a list or scalar) — heal fully.
            needs_write = True

    if needs_write:
        with open(CENTERS_FILE, 'w') as f:
            json.dump({'centers': _canonical_centers(),
                       'rotation_minutes': rotation}, f, indent=2)


def _load_config():
    """Load the full config from disk, ensuring validity first."""
    _ensure_config()
    try:
        with open(CENTERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError, OSError):
        # Extremely unlikely after _ensure_config, but stay safe.
        return {'centers': _canonical_centers(),
                'rotation_minutes': DEFAULT_ROTATION_MINUTES}


def _save_config(config):
    """Save the full config to disk. Centers are always forced canonical."""
    _ensure_config()
    rotation = _coerce_rotation_minutes(config.get('rotation_minutes'))
    if rotation is None:
        rotation = DEFAULT_ROTATION_MINUTES
    with open(CENTERS_FILE, 'w') as f:
        json.dump({'centers': _canonical_centers(),
                   'rotation_minutes': rotation}, f, indent=2)


# ============================================================
# PUBLIC API
# ============================================================

def get_centers():
    """Get the 4 fixed centers, ordered by 'order'."""
    return _load_config().get('centers', _canonical_centers())


def get_center(center_id):
    """Get a single center by ID, or None if not found."""
    for center in get_centers():
        if center['id'] == center_id:
            return center
    return None


def get_rotation_minutes():
    """Get the current rotation length in minutes (default 10)."""
    rotation = _coerce_rotation_minutes(_load_config().get('rotation_minutes'))
    if rotation is None:
        return DEFAULT_ROTATION_MINUTES
    return rotation


def set_rotation_minutes(n):
    """
    Set the rotation length in minutes.

    Input policy (coerce + clamp): numeric strings and whole-number floats
    are accepted and coerced to int, then clamped to the inclusive range
    5..30. Non-numeric / junk input (None, non-numeric string, fractional
    float, NaN/inf, bool) is rejected with a ValueError.

    Returns the value actually stored.
    """
    rotation = _coerce_rotation_minutes(n)
    if rotation is None:
        raise ValueError(
            "rotation_minutes must be a whole number (int, numeric string, "
            "or integer-valued float); got: {!r}".format(n)
        )
    config = _load_config()
    config['rotation_minutes'] = rotation
    _save_config(config)
    return rotation


def get_centers_config():
    """Get the full config dict: {'centers': [...], 'rotation_minutes': int}."""
    return _load_config()
