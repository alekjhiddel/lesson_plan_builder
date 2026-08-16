"""
Goal Bank Module — Pre-built IEP Goal Library
Kentucky-aligned goal templates organized by domain, skill area, and difficulty level.

Standards Alignment:
- MSD students: EFASAA (Extended Framework for Academic and Social Achievement Assessment)
- LBD students: KAS (Kentucky Academic Standards)
- Preschool: KYECS (Kentucky Early Childhood Standards) — 5 developmental domains

Each goal includes:
- Template text with [student] placeholder
- Measurement method
- SDI strategies
- Materials needed
- Difficulty level (1=foundational, 2=emerging, 3=developing, 4=approaching mastery)
"""

# ═══════════════════════════════════════════════════════════════════════════
# GOAL BANK DATA STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════

GOAL_BANK = {

    # ───────────────────────────────────────────────────────────────────────
    # COMMUNICATION DOMAIN
    # EFASAA: Communication strand / KAS: ELA Speaking & Listening
    # ───────────────────────────────────────────────────────────────────────
    'communication': {
        'display_name': 'Communication',
        'description': 'Receptive language, expressive language, pragmatics, AAC use',
        'standards_ref': {
            'MSD': 'EFASAA Communication Strand',
            'LBD': 'KAS ELA — Speaking & Listening Standards',
            'preschool': 'KYECS Communication Domain (C)',
        },
        'skill_areas': {

            'expressive_requesting': {
                'display_name': 'Expressive — Requesting/Manding',
                'goals': [
                    {
                        'id': 'comm_req_01',
                        'template': 'Given a desired item/activity within sight and a communication system, [student] will independently initiate a request using their AAC device/communication board in 8 out of 10 opportunities across 3 consecutive data days by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Opportunity-based data (+ / -)',
                            'frequency': 'Every requesting opportunity during structured activities',
                            'tool': 'Tally sheet with + (independent) / P (prompted) / - (no response)',
                            'criteria': '8/10 opportunities across 3 consecutive data days',
                        },
                        'sdi_strategies': [
                            'Time delay procedure (5-second wait before prompting)',
                            'Environmental arrangement (desired items visible but out of reach)',
                            'Least-to-most prompting hierarchy (gesture → model → partial physical → full physical)',
                            'Immediate reinforcement with requested item upon correct response',
                        ],
                        'materials': [
                            'AAC device or communication board with 20+ symbols',
                            'Highly preferred items/activities identified through preference assessment',
                            'Visual prompt cards for staff',
                            'Data collection tally sheet',
                        ],
                    },
                    {
                        'id': 'comm_req_02',
                        'template': 'Given a communication system with 30+ symbols and a natural opportunity, [student] will combine two symbols to make a specific request (e.g., "want + cookie," "more + swing") in 7 out of 10 opportunities across 3 data days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Opportunity-based data with specificity notation',
                            'frequency': 'All requesting opportunities across daily activities',
                            'tool': 'Data sheet recording: symbols used, prompted vs. independent, context',
                            'criteria': '7/10 opportunities with two-symbol combinations across 3 data days',
                        },
                        'sdi_strategies': [
                            'Aided language stimulation (model two-symbol combinations on the device)',
                            'Structured communication temptations across environments',
                            'Constant time delay (model → 5-sec delay → model again)',
                            'Natural reinforcement (honor all communication attempts)',
                        ],
                        'materials': [
                            'AAC device with organized vocabulary (core + fringe words)',
                            'Visual modeling strips showing two-symbol combinations',
                            'Preferred items for communication temptations',
                            'Staff training cards on aided language stimulation',
                        ],
                    },
                    {
                        'id': 'comm_req_03',
                        'template': 'Given a verbal model and up to 2 verbal prompts, [student] will verbally approximate a one-word request for a desired item in 6 out of 10 opportunities by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Trial data with verbal approximation noted',
                            'frequency': 'Minimum 5 opportunities per day during snack, play, and centers',
                            'tool': 'Recording sheet: verbal attempt (Y/N), approximation quality (1-3 scale), prompt level',
                            'criteria': '6/10 verbal approximations across varied settings',
                        },
                        'sdi_strategies': [
                            'Mand training with time delay',
                            'Phonological cueing (first sound provided)',
                            'Reinforcement for any verbal approximation',
                            'Paired verbal model with sign/gesture for multi-modal access',
                        ],
                        'materials': [
                            'Highly preferred reinforcers (edibles, toys, activities)',
                            'Visual first-then board (say word → get item)',
                            'Mirror for oral motor awareness',
                            'Recording/playback device for self-monitoring',
                        ],
                    },
                    {
                        'id': 'comm_req_04',
                        'template': 'Given access to a speech-generating device and natural communication opportunities throughout the school day, [student] will independently navigate to the correct category and select a symbol to request in 80% of communication opportunities across 5 consecutive school days by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Percentage of opportunities with navigation accuracy tracked',
                            'frequency': 'All communication attempts logged during school day',
                            'tool': 'Communication log: time, context, navigation accuracy, independence level',
                            'criteria': '80% accuracy across 5 consecutive school days',
                        },
                        'sdi_strategies': [
                            'Direct instruction on device navigation (category → item)',
                            'Motor planning practice (consistent icon placement)',
                            'Backward chaining for multi-step navigation sequences',
                            'Peer modeling of device use',
                        ],
                        'materials': [
                            'Speech-generating device (programmed with organized categories)',
                            'Category visual cue cards',
                            'Navigation practice activities (structured "treasure hunts")',
                            'Staff competency checklist for device support',
                        ],
                    },
                ],
            },

            'expressive_commenting': {
                'display_name': 'Expressive — Commenting/Labeling',
                'goals': [
                    {
                        'id': 'comm_com_01',
                        'template': 'Given a shared activity and a communication system, [student] will spontaneously comment on an item or event (label, describe, or share information) in 5 out of 10 opportunities across 3 data days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Opportunity-based recording during shared activities',
                            'frequency': 'Minimum 3 structured shared activities per day',
                            'tool': 'Tally sheet: spontaneous comment (S) / prompted (P) / no comment (-)',
                            'criteria': '5/10 spontaneous comments across 3 data days',
                        },
                        'sdi_strategies': [
                            'Create "commentable" moments (surprising events, novel items)',
                            'Model commenting on AAC during activities',
                            'Expectant pause (look expectantly at student + device)',
                            'Reinforcement for all commenting attempts (social praise, continued interaction)',
                        ],
                        'materials': [
                            'AAC with comment vocabulary (descriptors, emotions, observations)',
                            'Novel/surprising activity materials',
                            'Commenting visual scripts',
                            'Peer communication partners trained in wait time',
                        ],
                    },
                    {
                        'id': 'comm_com_02',
                        'template': 'Given a picture, object, or event and a verbal prompt ("What do you see?"), [student] will label or describe using 1-2 words/symbols in 7 out of 10 opportunities by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Discrete trial data during labeling activities',
                            'frequency': 'Daily during circle time and 1:1 sessions',
                            'tool': 'Trial sheet with accuracy and prompt level recorded',
                            'criteria': '7/10 correct labels across varied items/pictures',
                        },
                        'sdi_strategies': [
                            'Discrete trial training for labeling',
                            'Picture-to-symbol matching practice',
                            'Errorless learning (immediate model for new items)',
                            'Generalization probes across materials and settings',
                        ],
                        'materials': [
                            'Real objects and corresponding pictures/symbols',
                            'Category sorting mats',
                            'Labeling data sheets',
                            'Reinforcement menu visual',
                        ],
                    },
                ],
            },

            'receptive_language': {
                'display_name': 'Receptive Language',
                'goals': [
                    {
                        'id': 'comm_rec_01',
                        'template': 'Given a one-step verbal direction paired with a gesture or visual cue, [student] will follow the direction within 10 seconds in 8 out of 10 trials across 3 consecutive data days by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Trial-based data with latency recording',
                            'frequency': 'Minimum 10 directions per day across activities',
                            'tool': 'Data sheet: direction given, response (correct/incorrect), latency, prompt needed',
                            'criteria': '8/10 trials correct across 3 consecutive data days',
                        },
                        'sdi_strategies': [
                            'Ensure attention before delivering direction',
                            'Pair verbal with visual/gestural cue, fade over time',
                            'Use consistent language for routine directions',
                            'Immediate reinforcement for compliance within time frame',
                        ],
                        'materials': [
                            'Visual direction cards (picture + text)',
                            'Token board for compliance reinforcement',
                            'Timer (visual timer for student awareness)',
                            'Consistent routine direction list for staff',
                        ],
                    },
                    {
                        'id': 'comm_rec_02',
                        'template': 'Given a two-step direction with visual supports, [student] will complete both steps in sequence within 30 seconds in 7 out of 10 trials by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Task analysis data — both steps must be completed in order',
                            'frequency': 'Minimum 5 two-step directions per day',
                            'tool': 'Checklist: Step 1 (Y/N), Step 2 (Y/N), sequence correct (Y/N), prompt level',
                            'criteria': '7/10 both steps completed in sequence',
                        },
                        'sdi_strategies': [
                            'Visual sequence strips (first-then for two steps)',
                            'Backward chaining (help with step 1, student does step 2 independently)',
                            'Consistent two-step directions embedded in routines',
                            'Graduated prompt reduction (full → partial → gestural → independent)',
                        ],
                        'materials': [
                            'First-then visual boards',
                            'Routine-specific two-step visual strips',
                            'Sequencing practice materials',
                            'Staff cue card with consistent two-step direction examples',
                        ],
                    },
                    {
                        'id': 'comm_rec_03',
                        'template': 'Given a field of 4 items and a verbal direction to select a named item, [student] will correctly identify the requested item in 9 out of 10 trials across a minimum of 20 target items by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Discrete trial with field of 4',
                            'frequency': 'Daily 1:1 sessions (10 trials minimum)',
                            'tool': 'Trial data sheet with item presented, response, field arrangement rotated',
                            'criteria': '9/10 correct with position randomized, across 20+ target items',
                        },
                        'sdi_strategies': [
                            'Errorless learning progressing to delayed prompt',
                            'Systematic rotation of position in field',
                            'Expand field gradually (2 → 3 → 4)',
                            'Generalization across item types (real objects, photos, symbols)',
                        ],
                        'materials': [
                            'Object/picture sets organized by category',
                            'Field-of-4 data recording template',
                            'Position rotation guide for staff',
                            'Reinforcement items',
                        ],
                    },
                ],
            },

            'pragmatic_social_communication': {
                'display_name': 'Pragmatic/Social Communication',
                'goals': [
                    {
                        'id': 'comm_prag_01',
                        'template': 'Given a social greeting opportunity (arrival, departure, peer interaction) and a communication system, [student] will initiate or respond to a greeting within 5 seconds in 8 out of 10 opportunities across 5 school days by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Event recording during natural greeting opportunities',
                            'frequency': 'All arrival/departure and social opportunities',
                            'tool': 'Greeting log: initiated vs. responded, mode used, latency, prompt level',
                            'criteria': '8/10 opportunities with greeting across 5 school days',
                        },
                        'sdi_strategies': [
                            'Structured greeting routine (consistent expectation at transitions)',
                            'Peer buddy system for greeting practice',
                            'Social story about greetings',
                            'Visual/auditory cue at door to prompt greeting',
                        ],
                        'materials': [
                            'Greeting choice board (wave, high-five, fist bump, verbal, AAC)',
                            'Social story about greetings',
                            'Doorway visual cue (picture of greeting)',
                            'Peer greeting partner schedule',
                        ],
                    },
                    {
                        'id': 'comm_prag_02',
                        'template': 'Given a structured conversational exchange with a peer or adult and visual turn-taking supports, [student] will take 2 or more conversational turns (initiate/respond/add information) in 6 out of 10 structured opportunities by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Structured conversation probes',
                            'frequency': '2-3 structured opportunities per day',
                            'tool': 'Conversation log: # of turns, mode, topic maintenance, partner',
                            'criteria': '6/10 exchanges with 2+ turns',
                        },
                        'sdi_strategies': [
                            'Visual conversation scripts with turn-taking marker',
                            'Video modeling of back-and-forth exchanges',
                            'Structured conversation activities (show-and-tell, partner games)',
                            'AAC programmed with conversation starters and responses',
                        ],
                        'materials': [
                            'Turn-taking visual (whose turn to talk/listen)',
                            'Conversation topic cards with visuals',
                            'AAC conversation pages',
                            'Video models of peer conversations',
                        ],
                    },
                ],
            },
        },
    },

    # ───────────────────────────────────────────────────────────────────────
    # FUNCTIONAL / LIFE SKILLS DOMAIN
    # EFASAA: Functional Skills Strand
    # ───────────────────────────────────────────────────────────────────────
    'functional_life_skills': {
        'display_name': 'Functional / Life Skills',
        'description': 'Daily living, self-care, household tasks, community skills, independence',
        'standards_ref': {
            'MSD': 'EFASAA Functional Skills Strand',
            'LBD': 'KAS with functional application',
            'preschool': 'KYECS Adaptive Domain (A)',
        },
        'skill_areas': {

            'self_care_hygiene': {
                'display_name': 'Self-Care & Hygiene',
                'goals': [
                    {
                        'id': 'func_sc_01',
                        'template': 'Given a visual task analysis and up to 2 gestural prompts, [student] will independently complete all steps of hand-washing in correct sequence in 9 out of 10 opportunities across 5 school days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Task analysis checklist (each step scored independently)',
                            'frequency': 'Every hand-washing opportunity (minimum 4/day)',
                            'tool': '8-step task analysis: each step marked I (independent), G (gestural), V (verbal), PP (partial physical), FP (full physical)',
                            'criteria': 'All steps independent or gestural only, 9/10 opportunities across 5 days',
                        },
                        'sdi_strategies': [
                            'Visual task analysis posted at sink (waterproof laminated)',
                            'Forward chaining (teach step 1 to mastery, then add step 2)',
                            'Graduated guidance — physical prompt fading',
                            'Consistent verbal cues across all staff ("Check your list")',
                        ],
                        'materials': [
                            'Laminated visual task analysis at each sink',
                            'Step-by-step photo sequence',
                            'Self-monitoring checklist for student (check off each step)',
                            'Timer for appropriate duration',
                        ],
                    },
                    {
                        'id': 'func_sc_02',
                        'template': 'Given a visual schedule and personal hygiene supplies, [student] will complete a 5-step morning arrival routine (backpack → coat → folder → bathroom → seat) independently with no more than 1 verbal redirect in 8 out of 10 school days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Whole-task recording with prompt level per step',
                            'frequency': 'Daily at arrival',
                            'tool': 'Arrival routine checklist: steps completed, prompts needed, time to complete',
                            'criteria': '8/10 days with ≤1 verbal redirect for entire routine',
                        },
                        'sdi_strategies': [
                            'Consistent arrival routine with visual schedule at cubby',
                            'Video model of routine played on tablet during initial teaching',
                            'Peer model (arrive with typical peer who demonstrates)',
                            'Natural reinforcement — preferred activity available after routine completion',
                        ],
                        'materials': [
                            'Individual visual arrival schedule (Velcro or flip)',
                            'Labeled cubby with picture/name',
                            'Timer (visual countdown for pacing)',
                            'Reinforcement choice board for post-routine',
                        ],
                    },
                    {
                        'id': 'func_sc_03',
                        'template': 'Given visual supports and a structured toileting schedule, [student] will independently initiate a bathroom request or respond to a scheduled bathroom prompt and complete toileting with no more than 1 physical prompt in 80% of opportunities across 10 school days by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Toileting data log (scheduled + initiated)',
                            'frequency': 'Every toileting opportunity (scheduled every 60-90 min + initiated)',
                            'tool': 'Toileting log: time, initiated/scheduled, dry check, independence level, accidents',
                            'criteria': '80% of opportunities with ≤1 physical prompt across 10 days',
                        },
                        'sdi_strategies': [
                            'Systematic toileting schedule with visual timer',
                            'Communication symbol for bathroom always accessible',
                            'Positive reinforcement for dry checks AND successful toileting',
                            'Graduated physical prompt fading (full physical → partial → gestural)',
                        ],
                        'materials': [
                            'Visual toileting schedule with timer',
                            'Bathroom communication symbol (on AAC and portable card)',
                            'Toileting task analysis visual in bathroom',
                            'Reinforcement items specific to toileting success',
                            'Dry-check data log',
                        ],
                    },
                ],
            },

            'food_preparation': {
                'display_name': 'Food Preparation & Mealtime',
                'goals': [
                    {
                        'id': 'func_food_01',
                        'template': 'Given a visual recipe with 5 or fewer steps and pre-measured ingredients, [student] will independently complete a simple snack preparation task (e.g., spreading, pouring, assembling) in 4 out of 5 opportunities by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Task analysis per recipe step',
                            'frequency': 'Daily snack preparation (rotating recipes)',
                            'tool': 'Visual recipe checklist: each step rated by independence level',
                            'criteria': '4/5 complete recipes with all steps independent or gestural only',
                        },
                        'sdi_strategies': [
                            'Visual recipes with real photos of each step',
                            'Total task presentation (practice entire recipe each time)',
                            'Systematic instruction with constant time delay',
                            'Self-monitoring — student checks off each step',
                        ],
                        'materials': [
                            'Laminated visual recipes (3-5 per rotation)',
                            'Adaptive utensils as needed (built-up handles, non-slip mats)',
                            'Pre-portioned ingredient containers',
                            'Self-check visual strip',
                        ],
                    },
                    {
                        'id': 'func_food_02',
                        'template': 'Given appropriate utensils and a meal/snack, [student] will independently eat using a spoon/fork with minimal spillage (no more than 3 spills per meal) and use a napkin when prompted in 8 out of 10 meals by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Mealtime observation recording',
                            'frequency': 'Every meal/snack at school',
                            'tool': 'Mealtime data: utensil use (Y/N), spill count, napkin use (independent/prompted)',
                            'criteria': '8/10 meals meeting criteria (≤3 spills + utensil use)',
                        },
                        'sdi_strategies': [
                            'Adaptive utensils matched to motor needs',
                            'Hand-over-hand fading to independent scooping',
                            'Visual boundary on plate/tray (non-slip mat, plate guard)',
                            'Consistent verbal cue for napkin use before fading',
                        ],
                        'materials': [
                            'Adaptive utensils (weighted, built-up handle, angled)',
                            'Non-slip mat and plate guard',
                            'Visual mealtime routine strip',
                            'Napkin use visual cue card',
                        ],
                    },
                ],
            },

            'community_safety': {
                'display_name': 'Community & Safety Skills',
                'goals': [
                    {
                        'id': 'func_comm_01',
                        'template': 'Given community-based instruction opportunities and visual supports, [student] will demonstrate 3 safety skills (stop at curb, stay with group, identify exit signs) in 8 out of 10 CBI opportunities across 3 different community settings by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'CBI observation checklist',
                            'frequency': 'During all community-based instruction outings',
                            'tool': 'Safety skills checklist: each skill rated per CBI outing, setting noted',
                            'criteria': '8/10 CBI opportunities with all 3 skills demonstrated across 3 settings',
                        },
                        'sdi_strategies': [
                            'In-class practice with simulated environments before CBI',
                            'Social stories about community safety rules',
                            'Constant practice of "stop" response to verbal cue',
                            'Generalization across settings (school hallway → parking lot → store)',
                        ],
                        'materials': [
                            'Community safety social stories',
                            'Visual safety rule cards (portable, on lanyard)',
                            'Practice stop sign/curb simulation in classroom',
                            'CBI planning and data collection forms',
                        ],
                    },
                    {
                        'id': 'func_comm_02',
                        'template': 'Given a simulated or real store environment and a visual shopping list with pictures, [student] will locate and select 3 items from a list independently with no more than 1 gestural prompt per item in 4 out of 5 opportunities by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Task completion in community or simulated setting',
                            'frequency': 'Weekly CBI or simulated shopping practice',
                            'tool': 'Shopping checklist: items found (Y/N), prompts needed per item, setting',
                            'criteria': '4/5 shopping trips with all 3 items found (≤1 gestural prompt each)',
                        },
                        'sdi_strategies': [
                            'Systematic instruction: classroom simulation → school store → community store',
                            'Picture-to-real-item matching practice',
                            'Community-referenced instruction with repeated practice at same store',
                            'Peer buddy for natural support',
                        ],
                        'materials': [
                            'Visual shopping lists (picture + word)',
                            'Classroom "store" setup for practice',
                            'Real grocery store partner arrangement',
                            'Self-checkout practice materials',
                        ],
                    },
                ],
            },

            'money_time': {
                'display_name': 'Money & Time Concepts',
                'goals': [
                    {
                        'id': 'func_mt_01',
                        'template': 'Given a visual schedule with picture/symbol time markers, [student] will independently transition to the next activity within 2 minutes of the schedule cue in 8 out of 10 transitions across 5 school days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Transition latency recording',
                            'frequency': 'Every scheduled transition',
                            'tool': 'Transition data: time of cue, time student arrives at next activity, prompts',
                            'criteria': '8/10 transitions within 2 minutes across 5 days',
                        },
                        'sdi_strategies': [
                            'Visual schedule with moveable pieces (check off/move to "finished")',
                            'Auditory warning (timer chime 2 min before transition)',
                            'Consistent transition routine (cleanup → check schedule → go)',
                            'Reinforcement for quick transitions (beat the timer)',
                        ],
                        'materials': [
                            'Individual visual schedule (Velcro, flip, or digital)',
                            'Visual timer',
                            'Transition warning cards',
                            'Reinforcement for timely transitions',
                        ],
                    },
                    {
                        'id': 'func_mt_02',
                        'template': 'Given a "next dollar" strategy visual support and a purchase under $5, [student] will independently determine the correct number of dollar bills to pay in 8 out of 10 simulated or real purchasing opportunities by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Simulated and real purchasing trials',
                            'frequency': '3-5 trials per week (simulated and CBI)',
                            'tool': 'Trial data: price shown, dollars counted, correct (Y/N), setting',
                            'criteria': '8/10 correct payments across simulated and real settings',
                        },
                        'sdi_strategies': [
                            'Next-dollar strategy (round up to next whole dollar, count that many)',
                            'Price tag reading practice (identify dollar amount, ignore cents)',
                            'Systematic instruction with model → lead → test',
                            'Generalization from classroom to school store to community',
                        ],
                        'materials': [
                            'Next-dollar strategy visual reference card',
                            'Practice money (realistic dollar bills)',
                            'Price tag cards for practice',
                            'Classroom and school store setup',
                        ],
                    },
                ],
            },
        },
    },

    # ───────────────────────────────────────────────────────────────────────
    # ACADEMIC DOMAIN
    # EFASAA: Academic Strand / KAS: ELA + Math Standards
    # ───────────────────────────────────────────────────────────────────────
    'academic': {
        'display_name': 'Academic',
        'description': 'Functional academics (MSD) or grade-level with modifications (LBD)',
        'standards_ref': {
            'MSD': 'EFASAA Academic Strand (functional application of KAS)',
            'LBD': 'KAS — English Language Arts and Mathematics',
            'preschool': 'KYECS Cognitive Domain (B)',
        },
        'skill_areas': {

            'functional_reading': {
                'display_name': 'Functional Reading / Sight Words',
                'goals': [
                    {
                        'id': 'acad_read_01',
                        'template': 'Given a field of 4 printed words, [student] will correctly identify 20 functional sight words (safety/community words: EXIT, STOP, PUSH, PULL, DANGER, name, classroom labels) in 9 out of 10 trials across 3 data days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Discrete trial — word identification in field of 4',
                            'frequency': 'Daily during 1:1 literacy time (10 trials)',
                            'tool': 'Sight word data sheet: word presented, response, correct/incorrect, cumulative mastery',
                            'criteria': '9/10 correct identification across 3 data days per word set',
                        },
                        'sdi_strategies': [
                            'Systematic instruction with constant time delay (0-sec → 5-sec delay)',
                            'Word-to-picture matching progressing to word-only identification',
                            'Generalization practice (words on flash cards → environmental print → community)',
                            'Errorless learning for initial acquisition',
                        ],
                        'materials': [
                            'Functional sight word flash cards with picture support',
                            'Environmental print labels in classroom',
                            'Word-matching file folder activities',
                            'Sight word data tracking sheet (mastered/in progress/not introduced)',
                        ],
                    },
                    {
                        'id': 'acad_read_02',
                        'template': 'Given a short adapted text (2-3 sentences) with picture supports, [student] will answer 2 literal comprehension questions ("who" and "what") using their communication system in 7 out of 10 opportunities by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Comprehension probes after adapted reading',
                            'frequency': 'Daily shared reading time',
                            'tool': 'Comprehension response data: question type, response mode, correct/incorrect',
                            'criteria': '7/10 correct responses to who/what questions',
                        },
                        'sdi_strategies': [
                            'Adapted text with symbol supports (picture above key words)',
                            'Repeated reading (same text 3-5 times before comprehension probe)',
                            'Visual answer choices (field of 3 pictures for who/what)',
                            'Systematic questioning hierarchy (point to answer → select from field → generate)',
                        ],
                        'materials': [
                            'Adapted books with symbol supports (Tar Heel Reader, custom)',
                            'Comprehension question cards with visual answer choices',
                            'AAC programmed with answer vocabulary',
                            'Repeated reading schedule and data log',
                        ],
                    },
                    {
                        'id': 'acad_read_03',
                        'template': 'Given grade-level text with embedded supports (graphic organizers, vocabulary previews, text-to-speech), [student] will identify the main idea with 80% accuracy on curriculum-based measurement probes across 4 out of 5 assessment periods by the annual review date.',
                        'level': 3,
                        'population': 'LBD',
                        'measurement': {
                            'method': 'Curriculum-based measurement probes',
                            'frequency': 'Bi-weekly CBM probes',
                            'tool': 'CBM reading comprehension rubric aligned to KAS ELA standards',
                            'criteria': '80% accuracy across 4/5 assessment periods',
                        },
                        'sdi_strategies': [
                            'Graphic organizers for main idea and supporting details',
                            'Vocabulary pre-teaching before each text',
                            'Text-to-speech technology for decoding support',
                            'Explicit main idea strategy instruction (cover, recite, check)',
                        ],
                        'materials': [
                            'Grade-level text with embedded supports',
                            'Main idea graphic organizers',
                            'Vocabulary preview cards',
                            'Text-to-speech device/software',
                        ],
                    },
                ],
            },

            'functional_math': {
                'display_name': 'Functional Math / Numeracy',
                'goals': [
                    {
                        'id': 'acad_math_01',
                        'template': 'Given a set of objects (1-10) and a verbal direction, [student] will demonstrate 1:1 correspondence by touching and counting objects with 90% accuracy in 8 out of 10 trials across 3 data days by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Discrete trial counting probes',
                            'frequency': 'Daily during math centers (10 trials)',
                            'tool': 'Counting data: set size, correct count (Y/N), 1:1 correspondence maintained (Y/N)',
                            'criteria': '90% accuracy (correct final count + 1:1 touch) across 3 data days',
                        },
                        'sdi_strategies': [
                            'Hand-over-hand touch-counting fading to independent',
                            'Move-and-count strategy (move objects to "counted" pile)',
                            'Consistent count routine (touch, say, move)',
                            'Variety of materials to promote generalization',
                        ],
                        'materials': [
                            'Counting manipulatives (various textures, sizes, themes)',
                            'Counting mats with clear "counted" and "to count" sections',
                            'Number line for reference',
                            'Counting data recording sheet',
                        ],
                    },
                    {
                        'id': 'acad_math_02',
                        'template': 'Given two groups of objects (1-5 each) and a visual "more/less" choice board, [student] will correctly identify which group has "more" in 8 out of 10 trials across 5 data days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Discrete trial comparison probes',
                            'frequency': 'Daily math time (10 comparison trials)',
                            'tool': 'More/less data: groups presented, student choice, correct (Y/N)',
                            'criteria': '8/10 correct across 5 data days with varied set sizes',
                        },
                        'sdi_strategies': [
                            'Visual comparison mats (line up objects for visual comparison)',
                            'Start with very different quantities (1 vs 5), decrease difference over time',
                            'Consistent language ("Which has MORE? Point to MORE.")',
                            'Errorless to error-correction transition',
                        ],
                        'materials': [
                            'Comparison mats with clear sections',
                            'Varied manipulatives (preferred items for motivation)',
                            'More/less choice cards',
                            'Systematic quantity progression chart for staff',
                        ],
                    },
                    {
                        'id': 'acad_math_03',
                        'template': 'Given grade-level math word problems with visual representations and manipulative supports, [student] will correctly solve single-step addition and subtraction problems with 75% accuracy on weekly assessments across 4 out of 5 assessment periods by the annual review date.',
                        'level': 3,
                        'population': 'LBD',
                        'measurement': {
                            'method': 'Weekly math assessment (5-10 word problems)',
                            'frequency': 'Weekly assessment Friday',
                            'tool': 'KAS-aligned math assessment with rubric',
                            'criteria': '75% accuracy across 4/5 weekly assessments',
                        },
                        'sdi_strategies': [
                            'Visual representation strategy (draw it, model it, solve it)',
                            'Key word highlighting with caution about over-reliance',
                            'Manipulative use for concrete representation',
                            'Explicit strategy instruction (identify question → find information → choose operation → solve → check)',
                        ],
                        'materials': [
                            'Math manipulatives (counters, base-ten blocks)',
                            'Visual problem-solving graphic organizer',
                            'Word problem adapted for readability',
                            'Calculator for computation check',
                        ],
                    },
                ],
            },

            'writing_fine_motor': {
                'display_name': 'Writing / Fine Motor for Academics',
                'goals': [
                    {
                        'id': 'acad_write_01',
                        'template': 'Given a model and appropriate writing tool (adapted grip as needed), [student] will write their first name legibly (all letters recognizable, correct sequence) in 8 out of 10 trials without a model by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Name writing probes (with and without model)',
                            'frequency': 'Daily writing practice (3-5 trials)',
                            'tool': 'Name writing rubric: letters correct (count), sequence, legibility (1-3)',
                            'criteria': '8/10 trials with all letters correct, in sequence, legible, no model',
                        },
                        'sdi_strategies': [
                            'Highlighted/traced model → dotted → independent (fading supports)',
                            'Consistent starting dot and directional arrows',
                            'Multi-sensory practice (sand tray, finger paint, marker, pencil)',
                            'Name stamp or name card for self-checking',
                        ],
                        'materials': [
                            'Name writing practice sheets (highlighted → dotted → blank)',
                            'Adaptive writing tools (built-up pencil, slant board)',
                            'Name card model for self-reference',
                            'Multi-sensory materials (sand tray, wiki sticks, finger paint)',
                        ],
                    },
                    {
                        'id': 'acad_write_02',
                        'template': 'Given a sentence starter and a word bank with picture supports, [student] will compose and write/type a 3-5 word sentence independently in 7 out of 10 opportunities during journal time by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Writing sample analysis',
                            'frequency': 'Daily journal time',
                            'tool': 'Writing checklist: # words, sentence structure, independence level',
                            'criteria': '7/10 journal entries with 3-5 word sentence composed independently',
                        },
                        'sdi_strategies': [
                            'Sentence frame templates ("I like ___" "I see a ___")',
                            'Word bank with pictures organized by topic',
                            'Choice of writing modality (handwrite, stamp, type, dictate)',
                            'Gradual fading of sentence starters over time',
                        ],
                        'materials': [
                            'Sentence starter strips',
                            'Topic-specific word banks with pictures',
                            'Adapted journal (wide-ruled, highlighted lines)',
                            'Keyboard/tablet for typing option',
                        ],
                    },
                ],
            },
        },
    },

    # ───────────────────────────────────────────────────────────────────────
    # SOCIAL-EMOTIONAL DOMAIN
    # EFASAA: Social Skills Strand / KAS: Social-Emotional Learning
    # ───────────────────────────────────────────────────────────────────────
    'social_emotional': {
        'display_name': 'Social-Emotional',
        'description': 'Social interaction, emotional regulation, relationship skills, self-awareness',
        'standards_ref': {
            'MSD': 'EFASAA Social Skills Strand',
            'LBD': 'KAS Social-Emotional Learning Standards',
            'preschool': 'KYECS Social-Emotional Domain (D)',
        },
        'skill_areas': {

            'social_interaction': {
                'display_name': 'Social Interaction & Play',
                'goals': [
                    {
                        'id': 'se_int_01',
                        'template': 'Given a structured play activity with a peer and adult facilitation, [student] will engage in parallel or cooperative play for a minimum of 5 minutes with no more than 1 adult redirect in 7 out of 10 structured opportunities by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Duration recording during structured play',
                            'frequency': 'Daily structured social time (minimum 2 opportunities)',
                            'tool': 'Play data: duration of engagement, redirects needed, play level (parallel/cooperative), peer partner',
                            'criteria': '7/10 opportunities with 5+ minutes and ≤1 redirect',
                        },
                        'sdi_strategies': [
                            'Structured play activities with clear roles and materials',
                            'Peer buddy training (typical peers taught to initiate/respond)',
                            'Visual play scripts for common activities',
                            'Adult facilitation fading (high support → proximity → monitoring)',
                        ],
                        'materials': [
                            'Structured play activity cards with roles defined',
                            'Timer (visual) for engagement tracking',
                            'Peer buddy training materials',
                            'Preferred play items identified via preference assessment',
                        ],
                    },
                    {
                        'id': 'se_int_02',
                        'template': 'Given a small group activity (2-3 peers) and visual turn-taking supports, [student] will wait for their turn without disruptive behavior for up to 2 minutes in 8 out of 10 structured turn-taking opportunities by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Event recording during turn-taking activities',
                            'frequency': 'All small group activities with turn-taking',
                            'tool': 'Turn-taking data: wait time, disruptive behavior (Y/N), visual support used (Y/N)',
                            'criteria': '8/10 turns waited appropriately (no disruptive behavior during wait)',
                        },
                        'sdi_strategies': [
                            'Visual "my turn" / "wait" cards',
                            'Predictable turn order (visual sequence of who goes when)',
                            'Occupation during wait (fidget, hands-busy activity)',
                            'Immediate reinforcement for successful waiting',
                        ],
                        'materials': [
                            'Turn-taking visual (name cards in order)',
                            '"My turn" indicator (special hat, holder, card)',
                            'Wait time occupation items (fidgets, squeeze ball)',
                            'Social story about taking turns',
                        ],
                    },
                    {
                        'id': 'se_int_03',
                        'template': 'Given a social situation and visual social story, [student] will demonstrate appropriate personal space (arm\'s length from peers) during group activities in 8 out of 10 observed intervals across 5 school days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Interval recording during group activities',
                            'frequency': '10-minute observation during group activities (1-min intervals)',
                            'tool': 'Interval data: appropriate space maintained (Y/N) per 1-min interval',
                            'criteria': '8/10 intervals appropriate across 5 school days',
                        },
                        'sdi_strategies': [
                            'Hula hoop/rope circle visual for "my space"',
                            'Social story about personal space',
                            'Floor markers (tape/dots) showing where to stand/sit',
                            'Positive reinforcement for appropriate spacing',
                        ],
                        'materials': [
                            'Personal space social story',
                            'Floor markers (tape, carpet squares)',
                            'Visual "arm\'s length" reminder card',
                            'Hula hoop for concrete body boundary teaching',
                        ],
                    },
                ],
            },

            'emotional_regulation': {
                'display_name': 'Emotional Regulation & Self-Management',
                'goals': [
                    {
                        'id': 'se_reg_01',
                        'template': 'Given visual supports (emotion chart, calm-down sequence) and up to 1 adult verbal prompt, [student] will identify their emotional state using a visual scale or emotion card in 7 out of 10 opportunities when visibly dysregulated across 5 school days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Event recording during observed dysregulation',
                            'frequency': 'Every observed instance of emotional change/dysregulation',
                            'tool': 'Emotion identification log: trigger noted, emotion identified (Y/N), mode used, accuracy, prompt level',
                            'criteria': '7/10 opportunities with correct identification across 5 days',
                        },
                        'sdi_strategies': [
                            'Zones of Regulation adapted for cognitive level (color-coded)',
                            'Daily emotion check-ins (how are you feeling RIGHT NOW?)',
                            'Interoception activities (body scan — "my body feels…")',
                            'Model labeling emotions throughout the day',
                        ],
                        'materials': [
                            'Zones of Regulation visual (simplified)',
                            'Emotion choice board (4-6 basic emotions with photos)',
                            'Body map for interoception',
                            'Calm-down sequence visual strip',
                        ],
                    },
                    {
                        'id': 'se_reg_02',
                        'template': 'Given instruction in 3 calming strategies and visual cue cards, [student] will independently select and use a calming strategy (deep breaths, break space, squeeze tool) when upset or overstimulated, returning to baseline within 5 minutes in 6 out of 10 instances of dysregulation by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'ABC data with recovery time tracked',
                            'frequency': 'Every instance of observed dysregulation',
                            'tool': 'Behavior log: antecedent, behavior, strategy used (or not), time to return to baseline, adult support level',
                            'criteria': '6/10 instances with independent strategy use + return to baseline ≤5 min',
                        },
                        'sdi_strategies': [
                            'Explicit instruction in each strategy during calm state',
                            'Visual calm-down menu always accessible',
                            'Practice during non-stressful times (build muscle memory)',
                            'Staff de-escalation protocol (consistent across adults)',
                        ],
                        'materials': [
                            'Calm-down choice menu (visual with 3 strategy options)',
                            'Designated calm-down area with sensory tools',
                            'Visual countdown for deep breathing',
                            'Staff protocol card for consistent response',
                        ],
                    },
                ],
            },
        },
    },

    # ───────────────────────────────────────────────────────────────────────
    # BEHAVIORAL DOMAIN
    # 707 KAR 1:320, Section 5(3): Behavioral supports
    # ───────────────────────────────────────────────────────────────────────
    'behavioral': {
        'display_name': 'Behavioral',
        'description': 'Replacement behaviors, self-regulation, coping, positive behavioral supports',
        'standards_ref': {
            'MSD': '707 KAR 1:320, Section 5(3) — Positive behavioral interventions and supports',
            'LBD': '707 KAR 1:320, Section 5(3) — Positive behavioral interventions and supports',
            'preschool': 'KYECS Social-Emotional Domain (D) — Self-regulation',
        },
        'skill_areas': {

            'replacement_behaviors': {
                'display_name': 'Replacement Behaviors',
                'goals': [
                    {
                        'id': 'beh_rep_01',
                        'template': 'Given a frustrating or demanding task and access to a break request card/symbol, [student] will request a break using an appropriate communication method (instead of [target behavior: e.g., throwing materials, screaming]) in 8 out of 10 instances of observed frustration by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'ABC data with replacement behavior tracking',
                            'frequency': 'Every instance of frustration/demand avoidance observed',
                            'tool': 'Behavior data: antecedent, target behavior (Y/N), replacement behavior (Y/N), prompt level',
                            'criteria': '8/10 frustration instances result in appropriate break request',
                        },
                        'sdi_strategies': [
                            'Functional Communication Training (FCT)',
                            'Break card always accessible and within reach',
                            'Honor ALL break requests initially (teach function, then build tolerance)',
                            'Proactive offering of breaks before escalation',
                        ],
                        'materials': [
                            'Break request cards (multiple locations)',
                            'Break symbol on AAC device (easy access)',
                            'Designated break area with timer',
                            'Staff FCT protocol card',
                            'ABC data collection form',
                        ],
                    },
                    {
                        'id': 'beh_rep_02',
                        'template': 'Given social conflict or denied access to a preferred item/activity, [student] will use an appropriate protest/negotiation strategy (say "no thank you," request alternative, ask to wait) instead of [target behavior: e.g., aggression, property destruction] in 7 out of 10 observed instances by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Event recording of conflict situations',
                            'frequency': 'All observed denial/conflict situations',
                            'tool': 'Behavior log: situation, response (appropriate/inappropriate), strategy used, prompt level',
                            'criteria': '7/10 conflict situations resolved with appropriate strategy',
                        },
                        'sdi_strategies': [
                            'Social stories about what to do when told "no" or "wait"',
                            'Role play/practice during calm instructional time',
                            'Visual choice: "I can say no thank you, ask for something else, or ask to wait"',
                            'Differential reinforcement (heavy reinforcement for appropriate protest)',
                        ],
                        'materials': [
                            'Protest/negotiation visual choice cards',
                            'Social stories for common conflict scenarios',
                            'Role play scripts and materials',
                            'Reinforcement menu for appropriate conflict resolution',
                        ],
                    },
                ],
            },

            'task_compliance': {
                'display_name': 'Task Engagement & Compliance',
                'goals': [
                    {
                        'id': 'beh_task_01',
                        'template': 'Given a non-preferred task with visual supports (first-then board, timer, token board) and age-appropriate work expectations, [student] will remain engaged in the assigned task for 10 consecutive minutes with no more than 1 verbal redirect in 8 out of 10 work sessions by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Duration recording during work sessions',
                            'frequency': 'Every structured work session',
                            'tool': 'Work session data: duration of engagement, redirects, off-task behaviors, reinforcement earned',
                            'criteria': '8/10 sessions with 10+ minutes engagement and ≤1 redirect',
                        },
                        'sdi_strategies': [
                            'First-then board (work task → preferred activity)',
                            'Visual timer showing work duration',
                            'Token economy (earn tokens toward reinforcer)',
                            'Task interspersed with preferred activities (high-p sequence)',
                        ],
                        'materials': [
                            'First-then board',
                            'Visual timer',
                            'Token board (individualized)',
                            'Reinforcement menu updated regularly',
                        ],
                    },
                    {
                        'id': 'beh_task_02',
                        'template': 'Given an adult direction and up to 5 seconds of processing time, [student] will initiate compliance (begin the requested action) within 10 seconds in 8 out of 10 directions across the school day for 5 consecutive days by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Compliance data (initiation within 10 sec)',
                            'frequency': 'Sampled — 10 directions per day tracked (varied times/staff)',
                            'tool': 'Compliance tally: direction given, initiated within 10 sec (Y/N), completion, prompt needed',
                            'criteria': '8/10 directions initiated within 10 sec across 5 consecutive days',
                        },
                        'sdi_strategies': [
                            'Ensure attention before direction (say name, wait for eye contact/orientation)',
                            'Simple, clear, one-step directions',
                            'High-probability request sequence (easy → easy → easy → target)',
                            'Immediate praise/reinforcement for compliance',
                        ],
                        'materials': [
                            'Visual direction cards for common requests',
                            'Compliance data tracking form',
                            'Reinforcement items for immediate delivery',
                            'Staff cue card for high-p sequence examples',
                        ],
                    },
                ],
            },

            'self_monitoring': {
                'display_name': 'Self-Monitoring & Self-Management',
                'goals': [
                    {
                        'id': 'beh_self_01',
                        'template': 'Given a self-monitoring checklist with picture cues and an auditory signal (vibrating watch/timer), [student] will accurately self-rate their behavior (on-task/off-task) matching adult rating in 80% of intervals across 5 school days by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Inter-rater agreement between student and adult ratings',
                            'frequency': 'During targeted activity periods (3-4 per day)',
                            'tool': 'Self-monitoring sheet: student check (on/off) + adult check (on/off), agreement calculated',
                            'criteria': '80% agreement between student and adult ratings across 5 days',
                        },
                        'sdi_strategies': [
                            'Explicit instruction on "on-task" vs. "off-task" with video examples',
                            'Practice self-rating during non-contingent times first',
                            'Start with high agreement (reinforce matching), then fade adult checks',
                            'Vibrating watch/timer for discreet interval cues',
                        ],
                        'materials': [
                            'Self-monitoring checklist (picture-supported)',
                            'Vibrating watch or interval timer',
                            'On-task/off-task visual examples',
                            'Reinforcement for accurate self-monitoring (bonus for matching adult)',
                        ],
                    },
                ],
            },
        },
    },

    # ───────────────────────────────────────────────────────────────────────
    # MOTOR DOMAIN
    # EFASAA: Motor/Physical Strand / KAS: PE Standards
    # ───────────────────────────────────────────────────────────────────────
    'motor': {
        'display_name': 'Motor',
        'description': 'Fine motor, gross motor, sensory-motor, adaptive PE',
        'standards_ref': {
            'MSD': 'EFASAA Motor/Physical Strand',
            'LBD': 'KAS Physical Education Standards + OT/PT goals',
            'preschool': 'KYECS Physical Domain (E)',
        },
        'skill_areas': {

            'fine_motor': {
                'display_name': 'Fine Motor / Hand Skills',
                'goals': [
                    {
                        'id': 'motor_fine_01',
                        'template': 'Given adapted scissors and a variety of cutting tasks (lines, curves, shapes), [student] will cut along a line (within 1/4 inch of the line) for straight and curved cuts in 7 out of 10 trials by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Work sample analysis + trial data',
                            'frequency': 'Daily fine motor practice time',
                            'tool': 'Cutting rubric: within 1/4 inch (Y/N), line type (straight/curved), hand position noted',
                            'criteria': '7/10 cuts within 1/4 inch for both straight and curved',
                        },
                        'sdi_strategies': [
                            'Adapted scissors matched to hand strength/coordination (loop, spring-loaded, etc.)',
                            'Hand-over-hand fading to independent (physical → stabilizing → shadow → independent)',
                            'Thick lines → regular lines → complex shapes (progressive difficulty)',
                            'Bilateral coordination activities as warm-up',
                        ],
                        'materials': [
                            'Adapted scissors (spring-loaded, loop, left-hand)',
                            'Progressive cutting strips (thick lines → thin → curved → shapes)',
                            'Non-slip mat to stabilize paper',
                            'Fine motor warm-up materials (playdough, tongs, clothespins)',
                        ],
                    },
                    {
                        'id': 'motor_fine_02',
                        'template': 'Given a variety of functional fine motor tasks (zipping, buttoning, snapping, opening containers), [student] will independently complete 4 out of 5 dressing/packaging tasks presented without physical assistance by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Task completion probes across functional tasks',
                            'frequency': 'Daily during dressing practice and snack prep',
                            'tool': 'Functional fine motor checklist: task, independence level, time to complete',
                            'criteria': '4/5 functional tasks completed independently',
                        },
                        'sdi_strategies': [
                            'Practice with dressing frames (isolated skill before full garment)',
                            'OT consultation for adapted techniques',
                            'Forward chaining for multi-step fasteners',
                            'Daily repetition embedded in natural routines (coat on/off, lunch containers)',
                        ],
                        'materials': [
                            'Dressing frames (zipper, button, snap, buckle)',
                            'Practice vests/boards',
                            'Variety of container types for snack (twist, flip, zip, peel)',
                            'OT home program materials for carryover',
                        ],
                    },
                ],
            },

            'gross_motor': {
                'display_name': 'Gross Motor / Mobility',
                'goals': [
                    {
                        'id': 'motor_gross_01',
                        'template': 'Given an obstacle course with visual markers and verbal cues, [student] will navigate a 5-station gross motor course (climbing, balancing, jumping, crawling, throwing) completing all stations with no more than 1 physical assist in 7 out of 10 trials by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Station-by-station task analysis',
                            'frequency': 'Daily PE/gross motor time',
                            'tool': 'Obstacle course data: each station rated (independent, verbal cue, physical assist)',
                            'criteria': '7/10 courses completed with ≤1 physical assist total',
                        },
                        'sdi_strategies': [
                            'Visual station markers with picture of expected movement',
                            'PT-designed progression of difficulty',
                            'Consistent course layout for predictability (routine)',
                            'Peer modeling — follow a buddy through the course',
                        ],
                        'materials': [
                            'Adaptive PE equipment (balance beam, mats, targets)',
                            'Visual station cards with photos',
                            'Non-slip surfaces and safety padding',
                            'PT consultation schedule for modifications',
                        ],
                    },
                    {
                        'id': 'motor_gross_02',
                        'template': 'Given appropriate mobility equipment and environmental supports, [student] will independently navigate from classroom to 3 common school locations (cafeteria, bathroom, gym) using a consistent route in 9 out of 10 opportunities across 5 school days by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Route completion data with independence rating',
                            'frequency': 'Every transition to target locations',
                            'tool': 'Navigation log: destination, independent completion (Y/N), prompts, safety maintained',
                            'criteria': '9/10 independent navigation to all 3 locations across 5 days',
                        },
                        'sdi_strategies': [
                            'Consistent route with environmental markers (color-coded paths)',
                            'Systematic instruction: full escort → partial escort → monitoring → independent',
                            'Practice during low-traffic times before full independence',
                            'Safety protocol taught alongside navigation (stay right, stop at intersections)',
                        ],
                        'materials': [
                            'Visual map of routes (simplified)',
                            'Environmental markers (colored tape, picture landmarks)',
                            'Safety checklist for independent travel',
                            'Staff monitoring protocol during fading',
                        ],
                    },
                ],
            },

            'sensory_motor': {
                'display_name': 'Sensory-Motor Integration',
                'goals': [
                    {
                        'id': 'motor_sens_01',
                        'template': 'Given a structured sensory diet and visual cue card, [student] will independently request or initiate a sensory break using an appropriate method (card, AAC, verbal) before reaching a dysregulated state in 6 out of 10 observed opportunities by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Event recording with regulation state noted',
                            'frequency': 'All sensory break opportunities and dysregulation instances',
                            'tool': 'Sensory data: proactive request (Y/N), regulation state at request, activity at time, strategy chosen',
                            'criteria': '6/10 opportunities with proactive request BEFORE dysregulation',
                        },
                        'sdi_strategies': [
                            'OT-designed sensory diet with scheduled and as-needed activities',
                            'Interoception curriculum (recognizing body signals)',
                            'Visual sensory menu always accessible',
                            'Staff trained to recognize early signs of dysregulation and prompt',
                        ],
                        'materials': [
                            'Sensory break request card/symbol',
                            'Sensory menu (visual choices: swing, squeeze, headphones, walk, etc.)',
                            'Sensory diet schedule',
                            'Calm-down kit with OT-recommended items',
                        ],
                    },
                ],
            },
        },
    },

    # ───────────────────────────────────────────────────────────────────────
    # VOCATIONAL / TRANSITION DOMAIN
    # 707 KAR 1:320, Section 5(8) — Transition services (age 16+)
    # ───────────────────────────────────────────────────────────────────────
    'vocational_transition': {
        'display_name': 'Vocational / Transition',
        'description': 'Work readiness, job skills, self-determination, community access, post-secondary planning',
        'standards_ref': {
            'MSD': '707 KAR 1:320, Section 5(8) — Transition + EFASAA Vocational Strand',
            'LBD': '707 KAR 1:320, Section 5(8) — Transition + KAS Career Readiness',
            'preschool': 'N/A (transition begins at age 16)',
        },
        'skill_areas': {

            'work_readiness': {
                'display_name': 'Work Readiness & Task Completion',
                'goals': [
                    {
                        'id': 'voc_work_01',
                        'template': 'Given a structured work task with visual task analysis (3-5 steps) and a designated work area, [student] will independently complete the assigned job task to a quality standard (90% steps correct) in 8 out of 10 work sessions by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Task analysis with quality check',
                            'frequency': 'Daily work/vocational period',
                            'tool': 'Job task analysis: steps correct, quality (met standard Y/N), time, independence',
                            'criteria': '8/10 sessions with 90% steps correct to quality standard',
                        },
                        'sdi_strategies': [
                            'Systematic instruction on each job task step',
                            'Visual task analysis posted at work station',
                            'Self-monitoring checklist (student checks own work quality)',
                            'Rotating job tasks to build flexibility',
                        ],
                        'materials': [
                            'Visual task analyses for each job (laminated at station)',
                            'Quality standard reference card (what "done right" looks like)',
                            'Self-check clipboard',
                            'Reinforcement system tied to task completion',
                        ],
                    },
                    {
                        'id': 'voc_work_02',
                        'template': 'Given a work task and a visual timer, [student] will sustain on-task work behavior for 20 continuous minutes with no more than 1 verbal redirect in 8 out of 10 work sessions by the annual review date.',
                        'level': 3,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Duration of sustained work behavior',
                            'frequency': 'Daily work period',
                            'tool': 'Work duration data: minutes on-task, redirects, breaks taken',
                            'criteria': '8/10 sessions with 20+ min on-task and ≤1 redirect',
                        },
                        'sdi_strategies': [
                            'Gradually build endurance (5 min → 10 → 15 → 20)',
                            'Visual timer showing work period',
                            'Token economy (earn break/reinforcer after work period)',
                            'Alternate preferred and non-preferred task components',
                        ],
                        'materials': [
                            'Visual timer',
                            'Token board',
                            'Work period schedule strip (work → break → work → done)',
                            'Endurance building progression chart for staff',
                        ],
                    },
                ],
            },

            'self_determination': {
                'display_name': 'Self-Determination & Self-Advocacy',
                'goals': [
                    {
                        'id': 'voc_self_01',
                        'template': 'Given a daily choice-making opportunity and a visual choice board with 2-3 options, [student] will independently make a choice and communicate it using their preferred mode within 15 seconds in 9 out of 10 opportunities by the annual review date.',
                        'level': 1,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Choice-making data (latency + independence)',
                            'frequency': 'Minimum 5 choice opportunities per day (embedded)',
                            'tool': 'Choice data: options presented, choice made, mode used, latency, independent (Y/N)',
                            'criteria': '9/10 choices made independently within 15 seconds',
                        },
                        'sdi_strategies': [
                            'Embed choice-making throughout daily routine',
                            'Start with highly preferred vs. non-preferred (obvious choice), build to preference comparisons',
                            'Honor all choices made (build trust that choice = control)',
                            'Teach choice-making as a skill (look at options → point/press/say → get chosen item)',
                        ],
                        'materials': [
                            'Choice boards (2 option → 3 option) for various contexts',
                            'Varied materials for choice opportunities',
                            'Choice data tracking form',
                            'Staff prompt to offer choices (cue card at stations)',
                        ],
                    },
                    {
                        'id': 'voc_self_02',
                        'template': 'Given an unfamiliar task or confusing situation and access to a "help" symbol/card, [student] will appropriately request help (raise hand, press help button, give help card) instead of engaging in off-task or disruptive behavior in 7 out of 10 opportunities by the annual review date.',
                        'level': 2,
                        'population': 'MSD',
                        'measurement': {
                            'method': 'Event recording during challenging/unfamiliar tasks',
                            'frequency': 'All observed instances where help is needed',
                            'tool': 'Help-seeking data: situation, help requested (Y/N), mode used, appropriate (Y/N), off-task behavior (Y/N)',
                            'criteria': '7/10 help-needed situations resolved with appropriate request',
                        },
                        'sdi_strategies': [
                            'Functional Communication Training for "help" response',
                            'Help symbol always accessible (multiple locations)',
                            'Immediate adult response to help requests (reinforce the requesting)',
                            'Practice requesting help during instructional time (intentionally create need)',
                        ],
                        'materials': [
                            'Help cards/symbols at every work station',
                            'Help button on AAC device (easy access)',
                            'Practice scenarios for help-requesting',
                            'Staff protocol for responding to help requests immediately',
                        ],
                    },
                ],
            },
        },
    },

    # ───────────────────────────────────────────────────────────────────────
    # PRESCHOOL DEVELOPMENTAL GOALS
    # KYECS (Kentucky Early Childhood Standards) — 5 Domains
    # ───────────────────────────────────────────────────────────────────────
    'preschool': {
        'display_name': 'Preschool Developmental',
        'description': 'Five KYECS domains: Adaptive, Cognitive, Communication, Social-Emotional, Physical',
        'standards_ref': {
            'MSD': 'KYECS aligned with significant modifications',
            'LBD': 'KYECS with developmental delay supports',
            'preschool': 'KYECS (Kentucky Early Childhood Standards)',
        },
        'skill_areas': {

            'adaptive_preschool': {
                'display_name': 'Adaptive (KYECS Domain A)',
                'goals': [
                    {
                        'id': 'pre_adapt_01',
                        'template': 'Given consistent routine and visual supports, [student] will independently complete 3 self-help tasks during the school day (putting on coat, using napkin, washing hands) with no more than gestural prompts in 7 out of 10 opportunities by the annual review date.',
                        'level': 1,
                        'population': 'preschool',
                        'measurement': {
                            'method': 'Routine observation data',
                            'frequency': 'Daily during self-help opportunities',
                            'tool': 'Self-help checklist: task, prompt level, independence progression',
                            'criteria': '7/10 opportunities at gestural prompt or less for each of 3 tasks',
                        },
                        'sdi_strategies': [
                            'Consistent daily routine with embedded self-help expectations',
                            'Graduated guidance (physical → partial → gestural → independent)',
                            'Peer modeling during routine activities',
                            'Natural reinforcement (go outside after coat is on)',
                        ],
                        'materials': [
                            'Visual self-help steps posted at relevant locations',
                            'Adaptive clothing supports (larger zippers, Velcro)',
                            'Step stool at sink',
                            'Photo sequence of routine steps',
                        ],
                    },
                ],
            },

            'cognitive_preschool': {
                'display_name': 'Cognitive (KYECS Domain B)',
                'goals': [
                    {
                        'id': 'pre_cog_01',
                        'template': 'Given play-based learning activities with embedded instruction, [student] will demonstrate understanding of 3 basic concepts (big/little, in/out, on/off) by correctly demonstrating or identifying the concept in 8 out of 10 trials across play and structured activities by the annual review date.',
                        'level': 1,
                        'population': 'preschool',
                        'measurement': {
                            'method': 'Embedded trial data during play',
                            'frequency': 'Daily during structured play and circle time',
                            'tool': 'Concept data: concept targeted, correct demonstration (Y/N), setting/activity',
                            'criteria': '8/10 correct demonstrations per concept across activities',
                        },
                        'sdi_strategies': [
                            'Embedded instruction during naturally occurring activities',
                            'Multi-sensory concept teaching (show, do, feel, see)',
                            'Consistent language across all adults ("Show me IN")',
                            'Generalization across materials and settings',
                        ],
                        'materials': [
                            'Concept sorting materials (real objects, pictures)',
                            'Play materials that naturally embed concepts (containers, blocks)',
                            'Concept picture cards for adult reference',
                            'Concept books (in/out, big/little, etc.)',
                        ],
                    },
                    {
                        'id': 'pre_cog_02',
                        'template': 'Given cause-and-effect toys and activities with up to 1 model/demonstration, [student] will independently activate 5 different cause-and-effect items/activities (press button, pull string, flip switch) within 10 seconds of presentation in 8 out of 10 trials by the annual review date.',
                        'level': 1,
                        'population': 'preschool',
                        'measurement': {
                            'method': 'Trial data with latency recording',
                            'frequency': 'Daily during play centers',
                            'tool': 'Cause-effect data: item presented, response within 10 sec (Y/N), independent (Y/N)',
                            'criteria': '8/10 items activated independently within 10 sec',
                        },
                        'sdi_strategies': [
                            'High-interest cause-and-effect items based on preference assessment',
                            'Model → wait → prompt hierarchy',
                            'Environmental arrangement (items placed to encourage exploration)',
                            'Natural reinforcement (the effect IS the reinforcer)',
                        ],
                        'materials': [
                            'Variety of cause-effect toys (switch toys, pop-up, musical)',
                            'Adaptive switches for motor limitations',
                            'Exploration station with novel items rotated weekly',
                            'Preference assessment materials',
                        ],
                    },
                ],
            },

            'communication_preschool': {
                'display_name': 'Communication (KYECS Domain C)',
                'goals': [
                    {
                        'id': 'pre_comm_01',
                        'template': 'Given preferred activities and communication opportunities, [student] will use any intentional communication mode (gesture, sign, vocalization, AAC, word approximation) to make requests in 8 out of 10 communication opportunities across the school day by the annual review date.',
                        'level': 1,
                        'population': 'preschool',
                        'measurement': {
                            'method': 'Communication opportunity data',
                            'frequency': 'All communication opportunities (minimum 10/day)',
                            'tool': 'Communication log: opportunity, mode used, function (request/comment/protest), prompted/spontaneous',
                            'criteria': '8/10 opportunities with intentional communication',
                        },
                        'sdi_strategies': [
                            'Environmental arrangement to create communication need',
                            'Time delay (wait expectantly for communication)',
                            'Responsive interaction (honor all communication attempts)',
                            'Multi-modal modeling (pair words with signs/gestures/AAC)',
                        ],
                        'materials': [
                            'Communication system matched to motor/cognitive level',
                            'Preferred items for communication temptation',
                            'Visual supports for routines',
                            'Staff communication strategy cards',
                        ],
                    },
                ],
            },

            'social_emotional_preschool': {
                'display_name': 'Social-Emotional (KYECS Domain D)',
                'goals': [
                    {
                        'id': 'pre_se_01',
                        'template': 'Given adult-facilitated play with 1-2 peers and preferred activities, [student] will engage in interactive play (sharing materials, taking turns, or imitating peer actions) for a minimum of 3 minutes in 6 out of 10 structured opportunities by the annual review date.',
                        'level': 1,
                        'population': 'preschool',
                        'measurement': {
                            'method': 'Duration recording during structured peer play',
                            'frequency': '2-3 structured peer interactions per day',
                            'tool': 'Play data: duration of interactive play, play type (parallel/associative/cooperative), peer partner',
                            'criteria': '6/10 opportunities with 3+ minutes interactive play',
                        },
                        'sdi_strategies': [
                            'Adult-mediated peer interaction (facilitate, then fade)',
                            'Preferred materials that require two players',
                            'Peer modeling with trained typical peers',
                            'Visual play scripts for simple interactive games',
                        ],
                        'materials': [
                            'Two-player games and activities',
                            'Turn-taking toys (ball roll, car ramp)',
                            'Peer interaction visual supports',
                            'Timer for duration tracking',
                        ],
                    },
                ],
            },

            'physical_preschool': {
                'display_name': 'Physical (KYECS Domain E)',
                'goals': [
                    {
                        'id': 'pre_phys_01',
                        'template': 'Given developmentally appropriate fine motor activities and adaptive tools as needed, [student] will demonstrate functional grasp (palmar or tripod) to manipulate small objects (stacking 5 blocks, stringing 3 beads, completing 4-piece puzzle) in 7 out of 10 trials by the annual review date.',
                        'level': 1,
                        'population': 'preschool',
                        'measurement': {
                            'method': 'Fine motor task completion data',
                            'frequency': 'Daily fine motor center time',
                            'tool': 'Fine motor checklist: task, grasp type observed, completion (Y/N), adaptive tool used',
                            'criteria': '7/10 task completions with functional grasp',
                        },
                        'sdi_strategies': [
                            'OT-recommended grasp development activities',
                            'Adaptive tools matched to hand size/strength',
                            'Hand-over-hand fading to independent manipulation',
                            'High-interest materials for fine motor practice',
                        ],
                        'materials': [
                            'Stacking blocks (various sizes)',
                            'Lacing/stringing beads (large to small progression)',
                            'Puzzles (knob → inset → interlocking progression)',
                            'Adaptive tools (built-up crayons, adapted scissors, pencil grips)',
                        ],
                    },
                ],
            },
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# GOAL BANK API FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_all_domains():
    """Return list of all goal domains with metadata."""
    domains = []
    for domain_key, domain_data in GOAL_BANK.items():
        domains.append({
            'key': domain_key,
            'display_name': domain_data['display_name'],
            'description': domain_data['description'],
            'standards_ref': domain_data['standards_ref'],
            'skill_area_count': len(domain_data['skill_areas']),
            'total_goals': sum(
                len(sa['goals'])
                for sa in domain_data['skill_areas'].values()
            ),
        })
    return domains


def get_skill_areas(domain):
    """Return skill areas for a given domain."""
    if domain not in GOAL_BANK:
        return []
    domain_data = GOAL_BANK[domain]
    areas = []
    for area_key, area_data in domain_data['skill_areas'].items():
        areas.append({
            'key': area_key,
            'display_name': area_data['display_name'],
            'goal_count': len(area_data['goals']),
        })
    return areas


def get_goals(domain, skill_area=None, level=None, population=None):
    """
    Get goals filtered by domain, skill area, difficulty level, and/or population.

    Args:
        domain: Domain key (e.g., 'communication')
        skill_area: Optional skill area key (e.g., 'expressive_requesting')
        level: Optional difficulty level (1-4)
        population: Optional population filter ('MSD', 'LBD', 'preschool')

    Returns:
        List of matching goal dictionaries
    """
    if domain not in GOAL_BANK:
        return []

    results = []
    domain_data = GOAL_BANK[domain]

    for area_key, area_data in domain_data['skill_areas'].items():
        if skill_area and area_key != skill_area:
            continue

        for goal in area_data['goals']:
            if level and goal.get('level') != level:
                continue
            if population and goal.get('population', '').lower() != population.lower():
                continue

            results.append({
                **goal,
                'domain': domain,
                'domain_display': domain_data['display_name'],
                'skill_area': area_key,
                'skill_area_display': area_data['display_name'],
            })

    return results


def get_goal_by_id(goal_id):
    """Find a specific goal by its ID."""
    for domain_key, domain_data in GOAL_BANK.items():
        for area_key, area_data in domain_data['skill_areas'].items():
            for goal in area_data['goals']:
                if goal['id'] == goal_id:
                    return {
                        **goal,
                        'domain': domain_key,
                        'domain_display': domain_data['display_name'],
                        'skill_area': area_key,
                        'skill_area_display': area_data['display_name'],
                    }
    return None


def search_goals(query):
    """Search goals by keyword across all fields."""
    query_lower = query.lower()
    results = []

    for domain_key, domain_data in GOAL_BANK.items():
        for area_key, area_data in domain_data['skill_areas'].items():
            for goal in area_data['goals']:
                # Search in template text, SDI strategies, and materials
                searchable = ' '.join([
                    goal.get('template', ''),
                    ' '.join(goal.get('sdi_strategies', [])),
                    ' '.join(goal.get('materials', [])),
                    goal.get('measurement', {}).get('method', ''),
                ]).lower()

                if query_lower in searchable:
                    results.append({
                        **goal,
                        'domain': domain_key,
                        'domain_display': domain_data['display_name'],
                        'skill_area': area_key,
                        'skill_area_display': area_data['display_name'],
                    })

    return results


def personalize_goal(goal_id, student_name):
    """
    Return a goal with [student] replaced by the student's name.
    For use in actual IEP documents (after generation).
    """
    goal = get_goal_by_id(goal_id)
    if not goal:
        return None

    personalized = {**goal}
    personalized['template'] = goal['template'].replace('[student]', student_name)
    return personalized


def get_goals_count_summary():
    """Return a summary of how many goals are in each domain."""
    summary = {}
    for domain_key, domain_data in GOAL_BANK.items():
        total = sum(
            len(area_data['goals'])
            for area_data in domain_data['skill_areas'].values()
        )
        summary[domain_key] = {
            'display_name': domain_data['display_name'],
            'total_goals': total,
            'skill_areas': len(domain_data['skill_areas']),
        }
    return summary
