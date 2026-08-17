"""
SPARK - Break/Regulation Activity Bank
========================================
Curated sensory/motor break activities for MSD/autism classrooms.
Used by the schedule engine to auto-insert regulation breaks and
by teachers to pick appropriate activities for individual students.

Categories:
- movement: Gross motor activities
- deep_pressure: Proprioceptive input
- breathing: Calming breath exercises
- sensory: Tactile/visual/auditory regulation
- calm_down: Quiet regulation strategies

Each activity includes communication mode compatibility:
- verbal: Requires verbal instruction following
- visual: Can be taught with visual supports only
- physical: Uses hand-over-hand or modeling only
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ACTIVITY BANK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BREAK_ACTIVITIES = [
    # ─── MOVEMENT (Gross Motor) ───
    {
        "name": "Wall Push-Ups",
        "category": "movement",
        "duration_minutes": 3,
        "materials": "Wall",
        "communication_modes": ["verbal", "visual", "physical"],
        "description": "Student pushes against wall 10 times. Provides heavy work input."
    },
    {
        "name": "Animal Walks",
        "category": "movement",
        "duration_minutes": 5,
        "materials": "Open floor space",
        "communication_modes": ["verbal", "visual", "physical"],
        "description": "Bear walks, crab walks, frog jumps across the room."
    },
    {
        "name": "Chair Push-Ups",
        "category": "movement",
        "duration_minutes": 2,
        "materials": "Sturdy chair",
        "communication_modes": ["visual", "physical"],
        "description": "Student lifts body off chair using armrests. Quick proprioceptive input."
    },
    {
        "name": "Jump and Count",
        "category": "movement",
        "duration_minutes": 3,
        "materials": "None",
        "communication_modes": ["verbal", "visual", "physical"],
        "description": "Jump in place 10-20 times. Use visual countdown if needed."
    },
    {
        "name": "Hallway Walk",
        "category": "movement",
        "duration_minutes": 5,
        "materials": "Hallway pass",
        "communication_modes": ["verbal", "visual", "physical"],
        "description": "Structured walk with aide to specific destination and back."
    },
    {
        "name": "Stretching Routine",
        "category": "movement",
        "duration_minutes": 4,
        "materials": "Visual schedule card",
        "communication_modes": ["visual", "physical"],
        "description": "5-step stretch sequence: arms up, touch toes, twist, reach, shake."
    },

    # ─── DEEP PRESSURE (Proprioceptive) ───
    {
        "name": "Weighted Lap Pad",
        "category": "deep_pressure",
        "duration_minutes": 5,
        "materials": "Weighted lap pad (2-5 lbs)",
        "communication_modes": ["visual", "physical"],
        "description": "Place weighted pad on lap during seated work. Calming deep pressure."
    },
    {
        "name": "Body Squeeze (Hug Machine)",
        "category": "deep_pressure",
        "duration_minutes": 3,
        "materials": "Compression vest or self-hug",
        "communication_modes": ["physical"],
        "description": "Student gives self a tight squeeze or uses compression vest."
    },
    {
        "name": "Pillow Sandwich",
        "category": "deep_pressure",
        "duration_minutes": 5,
        "materials": "2 large floor pillows or crash pad",
        "communication_modes": ["visual", "physical"],
        "description": "Student lies between pillows with gentle pressure applied."
    },
    {
        "name": "Desk Push",
        "category": "deep_pressure",
        "duration_minutes": 2,
        "materials": "Heavy desk or table",
        "communication_modes": ["visual", "physical"],
        "description": "Push hands flat on desk and press hard for 10 seconds, repeat 5x."
    },
    {
        "name": "Carry Heavy Objects",
        "category": "deep_pressure",
        "duration_minutes": 5,
        "materials": "Books, water jugs, or weighted backpack",
        "communication_modes": ["verbal", "visual", "physical"],
        "description": "Deliver heavy items (books to library, water to office). Purposeful heavy work."
    },

    # ─── BREATHING (Calming) ───
    {
        "name": "Smell the Flower, Blow the Candle",
        "category": "breathing",
        "duration_minutes": 3,
        "materials": "Flower/candle visual card",
        "communication_modes": ["verbal", "visual", "physical"],
        "description": "Inhale through nose (smell flower), exhale through mouth (blow candle). 5 reps."
    },
    {
        "name": "Balloon Belly",
        "category": "breathing",
        "duration_minutes": 3,
        "materials": "None (visual card optional)",
        "communication_modes": ["verbal", "visual", "physical"],
        "description": "Hands on belly, breathe in to inflate balloon, slowly let air out."
    },
    {
        "name": "5-Finger Breathing",
        "category": "breathing",
        "duration_minutes": 3,
        "materials": "Hand (own or visual)",
        "communication_modes": ["visual", "physical"],
        "description": "Trace up each finger (breathe in), trace down (breathe out). 5 fingers = 5 breaths."
    },
    {
        "name": "Hoberman Sphere Breathing",
        "category": "breathing",
        "duration_minutes": 4,
        "materials": "Hoberman sphere (expandable ball)",
        "communication_modes": ["visual", "physical"],
        "description": "Expand sphere = breathe in, collapse = breathe out. Visual cue for pace."
    },
    {
        "name": "Pinwheel Blow",
        "category": "breathing",
        "duration_minutes": 3,
        "materials": "Pinwheel",
        "communication_modes": ["visual", "physical"],
        "description": "Blow pinwheel with slow, steady breaths. Reinforces controlled exhale."
    },

    # ─── SENSORY (Tactile/Visual/Auditory) ───
    {
        "name": "Fidget Bin Choice",
        "category": "sensory",
        "duration_minutes": 5,
        "materials": "Fidget bin (stress balls, putty, textured items)",
        "communication_modes": ["visual", "physical"],
        "description": "Student selects one fidget item from bin. Timer set for 5 min."
    },
    {
        "name": "Water Play",
        "category": "sensory",
        "duration_minutes": 5,
        "materials": "Bin of water, cups, sponges",
        "communication_modes": ["visual", "physical"],
        "description": "Pour, squeeze sponges, feel water temperature. Calming tactile input."
    },
    {
        "name": "Noise-Canceling Headphones",
        "category": "sensory",
        "duration_minutes": 5,
        "materials": "Noise-canceling headphones",
        "communication_modes": ["visual", "physical"],
        "description": "Reduce auditory input in overstimulating environments. Pair with calm corner."
    },
    {
        "name": "Playdough/Theraputty",
        "category": "sensory",
        "duration_minutes": 5,
        "materials": "Playdough or theraputty",
        "communication_modes": ["visual", "physical"],
        "description": "Squeeze, roll, pull apart. Combines tactile + proprioceptive input."
    },
    {
        "name": "Light Table Exploration",
        "category": "sensory",
        "duration_minutes": 5,
        "materials": "Light table + translucent objects",
        "communication_modes": ["visual", "physical"],
        "description": "Explore colored translucent blocks/shapes on illuminated surface."
    },
    {
        "name": "Vibrating Cushion",
        "category": "sensory",
        "duration_minutes": 5,
        "materials": "Vibrating seat cushion or handheld massager",
        "communication_modes": ["physical"],
        "description": "Vibration provides alerting or calming input depending on student."
    },

    # ─── CALM DOWN (Quiet Regulation) ───
    {
        "name": "Calm Corner Time",
        "category": "calm_down",
        "duration_minutes": 5,
        "materials": "Calm corner setup (bean bag, dim lighting, visual timer)",
        "communication_modes": ["visual", "physical"],
        "description": "Student goes to designated calm area. Timer visible. No demands placed."
    },
    {
        "name": "Picture Book Browse",
        "category": "calm_down",
        "duration_minutes": 5,
        "materials": "3-5 preferred picture books",
        "communication_modes": ["visual", "physical"],
        "description": "Look at preferred books independently. Low-demand downtime."
    },
    {
        "name": "Music with Headphones",
        "category": "calm_down",
        "duration_minutes": 5,
        "materials": "Tablet/phone with calming music playlist, headphones",
        "communication_modes": ["visual", "physical"],
        "description": "Listen to preferred calming music. Pair with weighted lap pad for max effect."
    },
    {
        "name": "Visual Timer Watch",
        "category": "calm_down",
        "duration_minutes": 3,
        "materials": "Visual countdown timer",
        "communication_modes": ["visual", "physical"],
        "description": "Student watches visual timer count down. Teaches waiting + provides predictability."
    },
    {
        "name": "Coloring/Scribble Sheet",
        "category": "calm_down",
        "duration_minutes": 5,
        "materials": "Paper and thick crayons/markers",
        "communication_modes": ["visual", "physical"],
        "description": "Free scribble or simple coloring page. No right/wrong. Process only."
    },
    {
        "name": "Body Scan Check-In",
        "category": "calm_down",
        "duration_minutes": 3,
        "materials": "Body outline visual card",
        "communication_modes": ["visual", "physical"],
        "description": "Point to body parts and check: tight? relaxed? Use emoji faces if needed."
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUBLIC API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_all_activities():
    """Return all break activities."""
    return BREAK_ACTIVITIES


def get_activities_by_category(category):
    """Get activities filtered by category."""
    return [a for a in BREAK_ACTIVITIES if a["category"] == category]


def get_categories():
    """Return list of available categories with descriptions."""
    return {
        "movement": "Gross motor activities (jumping, walking, stretching)",
        "deep_pressure": "Proprioceptive input (pushing, squeezing, heavy work)",
        "breathing": "Calming breath exercises with visual supports",
        "sensory": "Tactile, visual, or auditory regulation tools",
        "calm_down": "Quiet regulation strategies (calm corner, music, books)"
    }


def get_activities_for_student(student, duration_max=5):
    """
    Get appropriate activities for a specific student based on their
    communication mode and sensory preferences.
    
    Args:
        student: Student dict with communication_mode and sensory_needs
        duration_max: Maximum duration in minutes
        
    Returns:
        List of suitable activities
    """
    comm_mode = student.get("communication_mode", "visual")
    # Map student comm modes to activity compatibility
    mode_map = {
        "verbal": "verbal",
        "aac": "visual",
        "pecs": "visual",
        "sign": "visual",
        "gestural": "physical",
        "nonverbal": "physical"
    }
    required_mode = mode_map.get(comm_mode, "physical")
    
    suitable = []
    for activity in BREAK_ACTIVITIES:
        if required_mode in activity["communication_modes"]:
            if activity["duration_minutes"] <= duration_max:
                suitable.append(activity)
    
    return suitable


def get_random_break(category=None, duration_max=5, comm_mode=None):
    """
    Get a random activity, optionally filtered.
    Useful for the schedule engine auto-insertion.
    """
    import random
    candidates = BREAK_ACTIVITIES
    
    if category:
        candidates = [a for a in candidates if a["category"] == category]
    if duration_max:
        candidates = [a for a in candidates if a["duration_minutes"] <= duration_max]
    if comm_mode:
        candidates = [a for a in candidates if comm_mode in a["communication_modes"]]
    
    return random.choice(candidates) if candidates else None


def format_break_for_display(activity):
    """Format a single activity for display in the UI."""
    return {
        "name": activity["name"],
        "category": activity["category"].replace("_", " ").title(),
        "duration": f"{activity['duration_minutes']} min",
        "materials": activity["materials"],
        "modes": ", ".join(activity["communication_modes"]),
        "description": activity["description"]
    }
