"""
Help System Module
Provides in-app contextual help content. All help is stored locally
so it works offline. Each topic has an ID that can be linked from
? icons throughout the app.
"""

HELP_TOPICS = {
    'student_name': {
        'title': 'Student Name',
        'category': 'Student Profiles',
        'content': '<h2>Student Name</h2><p><strong>Privacy:</strong> This name is stored ONLY on your computer. When SPARK generates prompts for ChatGPT, it automatically replaces real names with "Child 1", "Child 2", etc. The real name is NEVER sent to any external service.</p><p>Use whatever name you normally call the student.</p>'
    },
    'communication_mode': {
        'title': 'Communication Mode',
        'category': 'Student Profiles',
        'content': '<h2>How Does This Student Communicate?</h2><p>Pick their primary communication mode:</p><ul><li><strong>Verbal</strong> - Speaks in sentences</li><li><strong>Limited verbal</strong> - Some words/phrases</li><li><strong>AAC device</strong> - Speech-generating device (TouchChat, LAMP, Proloquo2Go)</li><li><strong>PECS</strong> - Picture Exchange Communication System</li><li><strong>Sign language</strong> - ASL or modified signs</li><li><strong>Gestures/pointing</strong> - Points, leads, body language</li><li><strong>Non-verbal</strong> - No reliable communication yet</li><li><strong>Mixed</strong> - Multiple modes</li></ul><p><strong>In the details box:</strong> Be specific! "Uses TouchChat with 45-location page set, can request more, help, done, bathroom" is way more helpful than just "AAC device".</p><p><strong>Why this matters:</strong> SPARK uses this to make sure lesson plans include appropriate communication opportunities for this student.</p>'
    },
    'iep_goals': {
        'title': 'IEP Goals',
        'category': 'Student Profiles',
        'content': '<h2>IEP Goals</h2><p>Copy your student\'s measurable annual goals directly from their IEP. Separate each goal with a blank line.</p><h3>What makes a good measurable goal?</h3>
    },
    'behavioral_needs': {
        'title': 'Behavioral Needs',
        'category': 'Student Profiles',
        'content': '<h2>Behavioral Needs</h2><p>Include info from their BIP (Behavior Intervention Plan) if they have one.</p><h3>What to include:</h3><ul><li><strong>Triggers</strong> - What sets it off? (transitions, noise, demands)</li><li><strong>Behaviors</strong> - What does it look like? (elopement, hitting, screaming)</li><li><strong>Function</strong> - Why? (escape, attention, access, sensory)</li><li><strong>Prevention</strong> - What stops it? (visual warnings, choices, first-then)</li><li><strong>De-escalation</strong> - What calms them? (deep pressure, quiet space)</li><li><strong>Reinforcement</strong> - Token board details, schedule</li></ul><p><strong>Example:</strong> "Elopes when transitioning to non-preferred. Function: escape. Prevention: 2-min warning + timer + first-then. Token board: 5 stars = 3 min iPad. If elopement: block door calmly, redirect to schedule."</p>'
    },
    'sensory_needs': {
        'title': 'Sensory Needs',
        'category': 'Student Profiles',
        'content': '<h2>Sensory Needs</h2><p>Two types:</p><ul><li><strong>Sensory seeking</strong> - Craves input (jumping, crashing, mouthing, spinning)</li><li><strong>Sensory avoiding</strong> - Overwhelmed by input (covers ears, avoids touch)</li></ul><h3>Include:</h3><ul><li>What they seek and avoid</li><li>Sensory tools (weighted vest, headphones, chew toy, fidget)</li><li>OT recommendations (sensory diet, heavy work schedule)</li></ul><p><strong>Example:</strong> "Seeks deep pressure. Avoids loud sounds (use headphones for drills). Weighted lap pad for seated work. 5 min jumping before table activities."</p>'
    },
    'reinforcers': {
        'title': 'Reinforcers / Motivators',
        'category': 'Student Profiles',
        'content': '<h2>Reinforcers - What Makes This Kid Light Up?</h2><p>This is one of the MOST important fields. Knowing what motivates a student is the key to everything.</p><h3>Include:</h3><ul><li><strong>Primary</strong> - Food/drink (goldfish, juice, M&Ms)</li><li><strong>Activity</strong> - iPad, swinging, bubbles, music</li><li><strong>Social</strong> - Tickles, high-fives, specific praise</li><li><strong>Object</strong> - Spinning toys, favorite book</li><li><strong>Schedule</strong> - How often? Token system details?</li></ul><p><strong>Example:</strong> "LOVES iPad (YouTube nursery rhymes), bubbles, spinning objects. Token board: 5 tokens = 3 min iPad. Rotate iPad/bubbles to prevent satiation. Does NOT respond to stickers alone."</p><p><strong>Why:</strong> SPARK puts specific reinforcers into every aide plan so they know exactly what to offer.</p>'
    },
    'homeroom': {
        'title': 'Homeroom / Inclusion',
        'category': 'Student Profiles',
        'content': '<h2>Homeroom / Inclusion Time</h2><p>Kentucky students with disabilities are assigned to a gen ed homeroom. They may spend some time there.</p><h3>SPARK needs:</h3><ul><li><strong>Do they go?</strong> Some MSD students never attend.</li><li><strong>How long?</strong> 30 min? Half day?</li><li><strong>When?</strong> Morning? After lunch? For specials?</li><li><strong>Aide needed?</strong> Independent or escort required?</li></ul><p><strong>Why for scheduling:</strong> If a student leaves at 9:00 with an aide, that aide is unavailable for 30 min. The schedule solver needs this to prevent coverage gaps.</p>'
    },
    'life_skills': {
        'title': 'Life Skills Priorities',
        'category': 'Student Profiles',
        'content': '<h2>Life Skills Priorities</h2><p>For MSD students, the ultimate goal is maximum independence. These BIG skills determine quality of life.</p><h3>Categories:</h3><ul><li><strong>Self-care:</strong> Toileting, handwashing, dressing, eating</li><li><strong>Safety:</strong> Responding to name, stopping at roads</li><li><strong>Communication:</strong> Requesting needs, refusing, greeting</li><li><strong>Community:</strong> Waiting in line, public behavior</li><li><strong>Domestic:</strong> Simple food prep, cleaning</li><li><strong>Vocational:</strong> Task completion, following schedules</li></ul>'
    },
    'plan_type': {
        'title': 'Lesson Plan Types',
        'category': 'Lesson Plans',
        'content': '<h2>Lesson Plan Types</h2><h3>Full Weekly Plan</h3><p>Complete Monday-Friday: whole-group activities, center rotations, staff assignments, PLUS individual 1:1 aide plans per student per day.</p><h3>Daily Individual Plans Only</h3><p>Just the 1:1 aide plans - detailed enough for an aide to follow without verbal instruction. Use when you already have your classroom schedule set.</p>'
    },
    'themes': {
        'title': 'Seasonal Themes',
        'category': 'Lesson Plans',
        'content': '<h2>Seasonal Themes</h2><p>SPARK suggests themes based on the current month. Themes change MATERIALS but NOT skills.</p><p><strong>Example:</strong> "Sort by color" in October uses orange/black pumpkins. In February: red/pink hearts. Same skill, different wrapper!</p><p>Override with custom themes anytime - student interests work even better than seasonal defaults.</p>'
    },
    'schedule_coverage': {
        'title': 'Room Coverage Rules',
        'category': 'Scheduling',
        'content': '<h2>Room Coverage Rules</h2><p>Safety constraints:</p><ul><li>At least 1 aide in YOUR room at all times</li><li>At least 1 aide in partner room at all times (if applicable)</li><li>SPARK never assigns an escort that drops either room below minimum</li></ul><p>If there is a conflict, SPARK flags it and suggests staggering homeroom times.</p>'
    },
    'partner_export': {
        'title': 'Sharing with Partner Teacher',
        'category': 'Partner Teacher',
        'content': '<h2>Sharing with Your Partner</h2><p>Your partner gets operational info:</p><ul><li>Names, communication modes, physical needs</li><li>Behavioral triggers and de-escalation</li><li>Reinforcers, medical alerts, homeroom schedules</li></ul><p>Does NOT include: detailed IEP goals, progress data, private notes.</p><p>Both teachers are bound by FERPA - sharing between connected classrooms is normal.</p>'
    },
    'backup': {
        'title': 'Backing Up Your Data',
        'category': 'Data & Backup',
        'content': '<h2>Backing Up Your Data</h2><p><strong>How often?</strong> Weekly, or after big data entry sessions.</p><p><strong>Where to save:</strong></p><ul><li>USB drive (in a locked drawer)</li><li>External hard drive</li><li>NOT Google Drive, iCloud, Dropbox (FERPA!)</li></ul><p>The backup contains everything - student profiles, plans, settings. Restore it on a new machine to pick up where you left off.</p>'
    },
    'nti': {
        'title': 'NTI Packets',
        'category': 'NTI / Snow Days',
        'content': '<h2>NTI (Non-Traditional Instruction) Packets</h2><p>Snow days or school closures? SPARK generates individualized take-home packets considering:</p><ul><li>Communication mode (PECS kid gets picture activities, not worksheets)</li><li>Physical abilities (wheelchair user gets appropriate activities)</li><li>IEP goals (activities target real goals)</li><li>Parent resources (internet? printer? basic supplies?)</li></ul><p>Each packet includes simple parent instructions and optional data sheets.</p><p><strong>FAPE note:</strong> KY requires IEP services during NTI days. These packets document compliance.</p>'
    },
    'updates': {
        'title': 'Checking for Updates',
        'category': 'System',
        'content': '<h2>Keeping SPARK Up to Date</h2><ol><li>Go to Settings</li><li>Scroll to "Software Updates"</li><li>Click "Check for Updates"</li><li>If available, click "Download and Install"</li><li>Close window and re-launch SPARK</li></ol><p>Your data is always safe - updates only change code. A backup is created before every update.</p>'
    }
}


def get_help_topic(topic_id):
    """Get a specific help topic by ID."""
    return HELP_TOPICS.get(topic_id, {
        'title': 'Help',
        'category': 'General',
        'content': '<p>Help topic not found.</p>'
    })


def get_all_help_topics():
    """Get all help topics for the help index page."""
    return HELP_TOPICS


def get_help_categories():
    """Get help topics organized by category."""
    categories = {}
    for topic_id, topic in HELP_TOPICS.items():
        cat = topic.get('category', 'General')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({'id': topic_id, 'title': topic['title']})
    return categories
