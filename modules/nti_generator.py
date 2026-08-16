"""
SPARK - NTI (Non-Traditional Instruction) Packet Generator
Generates snow day / NTI packets individualized per student.

NTI packets must:
- Be aligned to each student's IEP goals
- Account for home resources (internet, printer, supplies)
- Use household items families already have
- Include parent instruction pages in simple language
- Provide appropriate activities based on disability category & cognitive level
- Track compliance for FAPE documentation

Activity Types by Population:
- MSD (IQ≤55): Matching, sorting household items, self-care practice,
  cause-effect, PECS practice, sensory activities with home materials
- LBD: Modified worksheets, reading practice, math problems, behavior self-monitoring
- Preschool: Play-based activities, songs, fine motor, language games
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import random


# ─────────────────────────────────────────────────────────────────────
# ACTIVITY BANKS BY POPULATION
# ─────────────────────────────────────────────────────────────────────

ACTIVITY_BANK = {
    'msd': {
        'communication': [
            {
                'title': 'Choice Making with Real Objects',
                'description': 'Hold up two items (snack choices, toy choices). Wait for your child to look at, reach for, or point to the one they want. Say the name of what they chose.',
                'materials': ['2 snack options or 2 toys from home'],
                'duration': '10-15 minutes',
                'data_prompt': 'How many times did your child make a choice? ___',
                'goal_areas': ['communication', 'choice_making']
            },
            {
                'title': 'Picture/Object Matching',
                'description': 'Use items from around the house (spoon, cup, sock, shoe). Lay out 2-3 items. Hold up a matching item and help your child find the match.',
                'materials': ['Pairs of household items (2 spoons, 2 socks, etc.)'],
                'duration': '10 minutes',
                'data_prompt': 'How many matches did your child make correctly? ___ out of ___',
                'goal_areas': ['communication', 'matching', 'cognitive']
            },
            {
                'title': 'PECS/Communication Board Practice',
                'description': 'During snack time, have your child use their communication board/book to request items. Help them point to or hand you the picture of what they want.',
                'materials': ['Communication board/book (from school backpack)', 'Preferred snacks'],
                'duration': '15 minutes (during snack)',
                'data_prompt': 'How many times did your child use their pictures to communicate? ___',
                'goal_areas': ['communication', 'pecs']
            },
            {
                'title': 'Responding to Name',
                'description': 'Call your child\'s name from across the room. Wait 5 seconds. If they look at you, give big praise! Try 5-10 times throughout the day.',
                'materials': ['No materials needed'],
                'duration': 'Throughout the day (2 minutes each time)',
                'data_prompt': 'How many times out of 10 did your child look when you called their name? ___/10',
                'goal_areas': ['communication', 'social']
            }
        ],
        'self_care': [
            {
                'title': 'Hand Washing Practice',
                'description': 'Practice washing hands before meals. Help your child: turn on water, get soap, rub hands, rinse, dry. Use the same steps every time. Let them do as much as they can alone!',
                'materials': ['Soap', 'Towel', 'Step stool if needed'],
                'duration': '5 minutes (before each meal)',
                'data_prompt': 'Which steps can your child do alone? (circle) Water on / Soap / Rub / Rinse / Dry',
                'goal_areas': ['self_care', 'daily_living']
            },
            {
                'title': 'Putting on Coat/Jacket',
                'description': 'Practice putting on a coat or zip-up jacket. Try the "flip trick": lay coat on floor with hood/tag toward child, child puts arms in and flips over head.',
                'materials': ['Coat or jacket'],
                'duration': '5-10 minutes',
                'data_prompt': 'How much help did your child need? (circle) Full help / Some help / Did it alone!',
                'goal_areas': ['self_care', 'motor']
            },
            {
                'title': 'Feeding Practice — Using a Spoon',
                'description': 'During a meal or snack, practice scooping with a spoon. Try thick foods first (yogurt, pudding, oatmeal). Hand-over-hand help is okay!',
                'materials': ['Spoon', 'Thick food (yogurt, pudding, oatmeal, applesauce)'],
                'duration': 'During mealtime',
                'data_prompt': 'How many bites did your child get to their mouth independently? ___',
                'goal_areas': ['self_care', 'motor', 'daily_living']
            },
            {
                'title': 'Sock and Shoe Practice',
                'description': 'Practice pulling socks up and/or putting shoes on. Start with the sock already mostly on — child just pulls it up the last bit. Build up to more independence.',
                'materials': ['Socks', 'Velcro shoes (if available)'],
                'duration': '5-10 minutes',
                'data_prompt': 'How much help needed? (circle) Full help / Started it for them / They did it alone',
                'goal_areas': ['self_care', 'daily_living']
            }
        ],
        'cognitive': [
            {
                'title': 'Sorting by Color',
                'description': 'Gather items of 2-3 different colors (socks, blocks, crayons, fruit). Make piles for each color. Help your child put items in the correct pile.',
                'materials': ['Colored items from home (socks, blocks, crayons, M&Ms)'],
                'duration': '10-15 minutes',
                'data_prompt': 'How many items did your child sort correctly? ___ out of ___',
                'goal_areas': ['cognitive', 'matching', 'sorting']
            },
            {
                'title': 'Cause and Effect — Push Toys & Switches',
                'description': 'Find toys or objects that DO something when you push/press them (light switch, musical toy, pop-up book). Help your child press the button and notice what happens!',
                'materials': ['Any push-button toy, light switch, or pop-up book'],
                'duration': '10-15 minutes',
                'data_prompt': 'Did your child push/press independently? Yes / With help / Needed hand-over-hand',
                'goal_areas': ['cognitive', 'cause_effect', 'motor']
            },
            {
                'title': 'Big vs. Little Sorting',
                'description': 'Find pairs of items in big and little sizes (big spoon/little spoon, big cup/little cup, big shoe/little shoe). Help your child sort into "big" and "little" piles.',
                'materials': ['Pairs of big and little household items'],
                'duration': '10 minutes',
                'data_prompt': 'How many did your child sort correctly? ___ out of ___',
                'goal_areas': ['cognitive', 'sorting', 'concepts']
            },
            {
                'title': 'Simple Puzzles or Shape Sorter',
                'description': 'Use any puzzle or shape sorter you have at home. If you don\'t have one, make a simple one: trace shapes on paper, child matches objects to outlines.',
                'materials': ['Puzzle, shape sorter, OR paper + crayons + objects to trace'],
                'duration': '10-15 minutes',
                'data_prompt': 'How many pieces/shapes did your child place correctly? ___',
                'goal_areas': ['cognitive', 'motor', 'matching']
            }
        ],
        'sensory_motor': [
            {
                'title': 'Sensory Bin with Kitchen Items',
                'description': 'Fill a bin/bowl with dry rice, pasta, or beans. Hide small toys or household items inside. Let your child dig, pour, scoop, and find hidden items.',
                'materials': ['Large bowl or bin', 'Dry rice/pasta/beans', 'Small toys or spoons'],
                'duration': '15-20 minutes',
                'data_prompt': 'How long did your child engage with the activity? ___ minutes',
                'goal_areas': ['sensory', 'motor', 'engagement']
            },
            {
                'title': 'Playdough Play (Homemade)',
                'description': 'Make playdough: 1 cup flour + 1/2 cup salt + 1/2 cup water + food coloring. Squeeze, roll, poke, flatten. Hide small items inside for child to find.',
                'materials': ['Flour', 'Salt', 'Water', 'Food coloring (optional)'],
                'duration': '20 minutes',
                'data_prompt': 'What did your child do with the playdough? (circle) Squeezed / Rolled / Poked / Pulled apart',
                'goal_areas': ['sensory', 'motor', 'engagement']
            },
            {
                'title': 'Movement Break — Animal Walks',
                'description': 'Do animal walks across the room: bear walk (hands and feet), crab walk, frog jumps, snake slither. Help your child copy you or do hand-over-hand.',
                'materials': ['Open floor space'],
                'duration': '10 minutes',
                'data_prompt': 'Which animal walks did your child try? ___',
                'goal_areas': ['motor', 'sensory', 'imitation']
            },
            {
                'title': 'Water Play',
                'description': 'Set up cups, spoons, and bowls near the sink or in a bin of water. Practice pouring, scooping, and splashing. Great for calming AND for motor skills.',
                'materials': ['Cups', 'Spoons', 'Bowls', 'Water', 'Towel for cleanup'],
                'duration': '15-20 minutes',
                'data_prompt': 'Did your child pour from one cup to another? Yes / With help / Not yet',
                'goal_areas': ['motor', 'sensory', 'daily_living']
            }
        ]
    },
    
    'lbd': {
        'reading': [
            {
                'title': 'Read Aloud (or Listen) for 15 Minutes',
                'description': 'Read a book together, have your child read to you, or listen to an audiobook. After reading, ask: Who was in the story? What happened?',
                'materials': ['Any book from home or school backpack'],
                'duration': '15-20 minutes',
                'data_prompt': 'Book title: ___ Pages read: ___ Could retell 1 thing? Yes / No',
                'goal_areas': ['reading', 'comprehension']
            },
            {
                'title': 'Sight Word Practice',
                'description': 'Write sight words on index cards or paper scraps. Practice reading them. Make it fun: hide them around the house for a word hunt!',
                'materials': ['Paper or index cards', 'Pencil/marker'],
                'duration': '10-15 minutes',
                'data_prompt': 'How many words could your child read? ___ out of ___',
                'goal_areas': ['reading', 'sight_words']
            },
            {
                'title': 'Write a Sentence',
                'description': 'Have your child write 2-3 sentences about their day. It\'s okay if spelling isn\'t perfect! The goal is putting thoughts into words.',
                'materials': ['Paper', 'Pencil'],
                'duration': '10-15 minutes',
                'data_prompt': 'How many sentences did your child write? ___',
                'goal_areas': ['writing', 'language']
            }
        ],
        'math': [
            {
                'title': 'Counting and Sorting',
                'description': 'Count items around the house: How many chairs? How many forks? Sort items by category and count each group.',
                'materials': ['Household items to count'],
                'duration': '10-15 minutes',
                'data_prompt': 'Highest number counted to correctly: ___',
                'goal_areas': ['math', 'counting']
            },
            {
                'title': 'Math Facts Practice',
                'description': 'Practice addition or subtraction facts. Use real objects to help (cereal pieces, coins, crayons). Write problems on paper or quiz verbally.',
                'materials': ['Paper and pencil', 'Small objects for counting'],
                'duration': '15 minutes',
                'data_prompt': 'How many problems completed? ___ How many correct? ___',
                'goal_areas': ['math', 'computation']
            },
            {
                'title': 'Money Skills',
                'description': 'Practice identifying coins and their values. Sort coins. If ready, practice adding coins together. Use real coins if available.',
                'materials': ['Real coins or drawn coins on paper'],
                'duration': '10-15 minutes',
                'data_prompt': 'Can identify: penny / nickel / dime / quarter (circle all)',
                'goal_areas': ['math', 'money', 'life_skills']
            }
        ],
        'behavior_self_monitoring': [
            {
                'title': 'Feelings Check-In',
                'description': 'Three times today, stop and check: "How am I feeling?" Draw a face or write the feeling. Practice a calming strategy if feeling upset.',
                'materials': ['Paper', 'Pencil/crayons'],
                'duration': '5 minutes, 3 times per day',
                'data_prompt': 'Feelings checked: Morning___ Afternoon___ Evening___',
                'goal_areas': ['behavior', 'self_regulation', 'social_emotional']
            },
            {
                'title': 'Following Directions Practice',
                'description': 'Give your child 1-2 step directions throughout the day. Start simple ("Put your plate in the sink") and build up. Praise when they follow through!',
                'materials': ['No materials needed'],
                'duration': 'Throughout the day',
                'data_prompt': 'How many directions followed on first try? ___ out of ___',
                'goal_areas': ['behavior', 'compliance', 'listening']
            }
        ]
    },
    
    'preschool': {
        'language': [
            {
                'title': 'Sing Songs Together',
                'description': 'Sing 3-5 favorite songs with your child. Do the motions! (Itsy Bitsy Spider, Wheels on the Bus, Head Shoulders Knees and Toes). Pause and let them fill in words.',
                'materials': ['No materials needed — just your voice!'],
                'duration': '10-15 minutes',
                'data_prompt': 'Songs we sang: ___ Did your child sing along or do motions? Yes / Some / Not yet',
                'goal_areas': ['language', 'communication', 'motor']
            },
            {
                'title': 'Name Things Around the House',
                'description': 'Walk around your home and name things together. Point to objects and say "What\'s this?" If your child can\'t say it yet, YOU say it and have them try to copy.',
                'materials': ['No materials needed'],
                'duration': '10 minutes',
                'data_prompt': 'How many items could your child name? ___',
                'goal_areas': ['language', 'vocabulary']
            },
            {
                'title': 'Read a Story (or Tell One)',
                'description': 'Read a picture book, or just tell a story using pictures. Point to pictures and name what you see. Ask your child to point to things you name.',
                'materials': ['Any picture book, magazine, or even food boxes with pictures'],
                'duration': '10-15 minutes',
                'data_prompt': 'Could your child point to pictures you named? Yes / Some / Not yet',
                'goal_areas': ['language', 'comprehension', 'vocabulary']
            }
        ],
        'fine_motor': [
            {
                'title': 'Coloring and Scribbling',
                'description': 'Let your child color, scribble, or draw. Any marks on paper are great! Try different tools: crayons, markers, chalk outside.',
                'materials': ['Paper', 'Crayons or markers'],
                'duration': '10-15 minutes',
                'data_prompt': 'How long did your child color? ___ minutes. Hand used most: Left / Right',
                'goal_areas': ['fine_motor', 'pre_writing']
            },
            {
                'title': 'Sticker Activity',
                'description': 'Peel stickers and put them on paper. Great for pinching fingers! Draw circles on paper and have your child put stickers inside the circles.',
                'materials': ['Stickers (any kind)', 'Paper'],
                'duration': '10 minutes',
                'data_prompt': 'Could your child peel stickers alone? Yes / Needed help starting them',
                'goal_areas': ['fine_motor', 'hand_strength']
            },
            {
                'title': 'Tearing and Crumpling Paper',
                'description': 'Tear paper into pieces (great for hand strength!). Crumple pieces into balls. Throw them into a bowl/bucket. Make it a game!',
                'materials': ['Old newspaper, junk mail, or plain paper', 'Bowl or bucket'],
                'duration': '10 minutes',
                'data_prompt': 'Could your child tear paper independently? Yes / Needed help starting',
                'goal_areas': ['fine_motor', 'hand_strength']
            }
        ],
        'play_social': [
            {
                'title': 'Pretend Play',
                'description': 'Play pretend together! Ideas: pretend to cook food, have a tea party, play store, be animals, play with dolls/figures. Follow your child\'s lead.',
                'materials': ['Toys, kitchen items, or imagination!'],
                'duration': '15-20 minutes',
                'data_prompt': 'What did your child pretend to do? ___',
                'goal_areas': ['play', 'social', 'language', 'imagination']
            },
            {
                'title': 'Turn-Taking Game',
                'description': 'Play a simple turn-taking game: roll a ball back and forth, stack blocks taking turns, or take turns putting items in a bucket. Say "My turn!" and "Your turn!"',
                'materials': ['Ball, blocks, or bucket with small toys'],
                'duration': '10-15 minutes',
                'data_prompt': 'How many turns did your child take? ___ Did they wait for their turn? Yes / Sometimes / Not yet',
                'goal_areas': ['social', 'play', 'turn_taking']
            }
        ],
        'gross_motor': [
            {
                'title': 'Dance Party!',
                'description': 'Put on music and dance! Practice jumping, spinning, stomping, clapping. Freeze when the music stops!',
                'materials': ['Music (phone, radio, or just sing!)'],
                'duration': '10-15 minutes',
                'data_prompt': 'Movements your child did: Jump / Spin / Stomp / Clap / Freeze (circle all)',
                'goal_areas': ['gross_motor', 'listening', 'sensory']
            },
            {
                'title': 'Obstacle Course',
                'description': 'Make a simple obstacle course: crawl under a table, step over a pillow, jump on a towel, throw a sock in a basket. Go through it together!',
                'materials': ['Pillows, towels, chairs, baskets — things from home'],
                'duration': '15-20 minutes',
                'data_prompt': 'Could your child complete the course? With help / Mostly alone / All alone!',
                'goal_areas': ['gross_motor', 'following_directions', 'body_awareness']
            }
        ]
    }
}

# Digital/internet activities supplement
DIGITAL_ACTIVITIES = {
    'msd': [
        {'title': 'Cause & Effect Apps', 'description': 'Try free cause-effect apps: Baby Sensory, Infant Zoo, or YouTube sensory videos. Let your child tap the screen and see what happens.', 'url_suggestions': ['YouTube: "sensory videos for autism"', 'App: Baby Sensory (free)']},
        {'title': 'Music Videos for Movement', 'description': 'Play Sesame Street or Wiggles videos. Encourage your child to clap, stomp, or dance along.', 'url_suggestions': ['YouTube: Sesame Street songs', 'YouTube: GoNoodle']},
    ],
    'lbd': [
        {'title': 'Khan Academy Kids', 'description': 'Free app with reading, math, and social-emotional activities. Tracks progress!', 'url_suggestions': ['App: Khan Academy Kids (free)', 'khanacademy.org/kids']},
        {'title': 'Starfall Reading', 'description': 'Free reading practice with phonics, stories, and games.', 'url_suggestions': ['starfall.com (free section)']},
        {'title': 'Math Games', 'description': 'Practice math facts with online games.', 'url_suggestions': ['coolmathgames.com', 'App: Moose Math (free)']},
    ],
    'preschool': [
        {'title': 'PBS Kids Games', 'description': 'Free educational games with familiar characters. Focus on letters, numbers, and problem-solving.', 'url_suggestions': ['pbskids.org', 'App: PBS Kids Games (free)']},
        {'title': 'GoNoodle Movement Videos', 'description': 'Fun movement videos for kids. Great indoor exercise!', 'url_suggestions': ['YouTube: GoNoodle', 'gonoodle.com (free)']},
    ]
}


# ─────────────────────────────────────────────────────────────────────
# NTI PACKET GENERATION
# ─────────────────────────────────────────────────────────────────────

def generate_nti_packet(student: dict, num_days: int = 1,
                        nti_date: str = None) -> dict:
    """
    Generate a complete NTI packet for one student.
    
    Args:
        student: Student dict with keys:
            - first_name, last_name, parent_name
            - disability_category: 'msd', 'lbd', or 'preschool'
            - communication_mode: 'verbal', 'pecs', 'device', 'gestures'
            - physical_needs: list (e.g., ['wheelchair', 'hand-over-hand'])
            - cognitive_level: approximate level description
            - iep_goals: list of goal dicts
            - home_resources: dict with 'internet', 'printer', 'supplies' booleans
            - grade, classroom
        num_days: Number of NTI days to generate (1-5)
        nti_date: Start date of NTI (defaults to tomorrow)
        
    Returns:
        dict with complete NTI packet data
    """
    if not nti_date:
        nti_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    first_name = student.get('first_name', 'Student')
    category = student.get('disability_category', 'msd').lower()
    home_resources = student.get('home_resources', {})
    has_internet = home_resources.get('internet', False)
    iep_goals = student.get('iep_goals', [])
    
    # Select activities for each day
    days = []
    used_activities = set()  # Track to avoid repeats across days
    
    for day_num in range(1, num_days + 1):
        day_date = _calculate_day_date(nti_date, day_num)
        activities = _select_activities_for_day(
            student, category, iep_goals, used_activities, has_internet
        )
        days.append({
            'day_number': day_num,
            'date': day_date,
            'activities': activities
        })
    
    # Build the packet
    packet = {
        'student': {
            'name': f"{first_name} {student.get('last_name', '')}".strip(),
            'first_name': first_name,
            'id': student.get('id'),
            'category': category,
            'communication_mode': student.get('communication_mode', 'verbal'),
            'grade': student.get('grade', ''),
            'classroom': student.get('classroom', '')
        },
        'parent_name': student.get('parent_name', 'Parent/Guardian'),
        'num_days': num_days,
        'start_date': nti_date,
        'days': days,
        'parent_instructions': _generate_parent_instructions(student, category),
        'data_sheet': _generate_data_sheet(days, first_name),
        'digital_suggestions': _get_digital_suggestions(category) if has_internet else None,
        'generated_at': datetime.now().isoformat(),
        'compliance': {
            'packet_generated': True,
            'generated_date': datetime.now().isoformat(),
            'student_id': student.get('id'),
            'num_days': num_days,
            'fape_documented': True
        }
    }
    
    return packet


def generate_class_nti_packets(students: list, num_days: int = 1,
                                nti_date: str = None) -> dict:
    """
    Generate NTI packets for an entire class at once.
    
    Args:
        students: List of student dicts
        num_days: Number of NTI days
        nti_date: Start date of NTI
        
    Returns:
        dict with all packets and summary
    """
    packets = []
    errors = []
    
    for student in students:
        try:
            packet = generate_nti_packet(student, num_days, nti_date)
            packets.append(packet)
        except Exception as e:
            errors.append({
                'student': student.get('first_name', 'Unknown'),
                'error': str(e)
            })
    
    return {
        'packets': packets,
        'summary': {
            'total_students': len(students),
            'packets_generated': len(packets),
            'errors': len(errors),
            'error_details': errors,
            'num_days': num_days,
            'start_date': nti_date or (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat()
        },
        'compliance_log': {
            'event': 'nti_packets_generated',
            'date': datetime.now().isoformat(),
            'num_students': len(packets),
            'num_days': num_days,
            'all_students_covered': len(errors) == 0
        }
    }


# ─────────────────────────────────────────────────────────────────────
# ACTIVITY SELECTION ENGINE
# ─────────────────────────────────────────────────────────────────────

def _select_activities_for_day(student: dict, category: str,
                                iep_goals: list, used: set,
                                has_internet: bool) -> list:
    """
    Select 3-5 appropriate activities for one NTI day.
    Prioritizes activities aligned to IEP goals.
    """
    category_bank = ACTIVITY_BANK.get(category, ACTIVITY_BANK['msd'])
    goal_areas = _extract_goal_areas(iep_goals)
    
    selected = []
    target_count = random.randint(3, 5)
    
    # First pass: find activities aligned to IEP goals
    for area, activities in category_bank.items():
        for activity in activities:
            if len(selected) >= target_count:
                break
            
            activity_id = activity['title']
            if activity_id in used:
                continue
            
            # Check if activity aligns with any IEP goal
            activity_goals = activity.get('goal_areas', [])
            if any(g in goal_areas for g in activity_goals):
                selected.append(_prepare_activity(activity, area))
                used.add(activity_id)
        
        if len(selected) >= target_count:
            break
    
    # Second pass: fill remaining slots with variety
    if len(selected) < 3:
        all_activities = []
        for area, activities in category_bank.items():
            for activity in activities:
                if activity['title'] not in used:
                    all_activities.append((activity, area))
        
        random.shuffle(all_activities)
        for activity, area in all_activities:
            if len(selected) >= target_count:
                break
            selected.append(_prepare_activity(activity, area))
            used.add(activity['title'])
    
    # Add one digital activity if internet available
    if has_internet and len(selected) < 5:
        digital = DIGITAL_ACTIVITIES.get(category, [])
        if digital:
            dig_activity = random.choice(digital)
            if dig_activity['title'] not in used:
                selected.append({
                    'title': dig_activity['title'],
                    'description': dig_activity['description'],
                    'materials': ['Device with internet (phone, tablet, or computer)'],
                    'duration': '15-20 minutes',
                    'data_prompt': 'How long did your child use the app/site? ___ minutes',
                    'category': 'digital',
                    'is_digital': True,
                    'url_suggestions': dig_activity.get('url_suggestions', [])
                })
                used.add(dig_activity['title'])
    
    return selected


def _prepare_activity(activity: dict, area: str) -> dict:
    """Prepare an activity dict for inclusion in packet."""
    return {
        'title': activity['title'],
        'description': activity['description'],
        'materials': activity.get('materials', []),
        'duration': activity.get('duration', '10-15 minutes'),
        'data_prompt': activity.get('data_prompt', ''),
        'category': area,
        'is_digital': False,
        'goal_areas': activity.get('goal_areas', [])
    }


def _extract_goal_areas(iep_goals: list) -> set:
    """Extract goal area keywords from IEP goals."""
    areas = set()
    for goal in iep_goals:
        area = goal.get('area', '').lower()
        # Map common IEP goal areas to activity bank categories
        area_mappings = {
            'communication': ['communication', 'pecs', 'language', 'vocabulary'],
            'self-care': ['self_care', 'daily_living'],
            'self care': ['self_care', 'daily_living'],
            'daily living': ['self_care', 'daily_living'],
            'adaptive': ['self_care', 'daily_living'],
            'motor': ['motor', 'fine_motor', 'gross_motor'],
            'fine motor': ['fine_motor', 'motor'],
            'gross motor': ['gross_motor', 'motor'],
            'cognitive': ['cognitive', 'matching', 'sorting'],
            'academic': ['reading', 'math', 'writing'],
            'reading': ['reading', 'comprehension', 'sight_words'],
            'math': ['math', 'counting', 'money'],
            'behavior': ['behavior', 'self_regulation', 'social_emotional'],
            'social': ['social', 'play', 'turn_taking'],
            'play': ['play', 'social', 'imagination'],
            'sensory': ['sensory', 'engagement'],
        }
        
        for key, mapped_areas in area_mappings.items():
            if key in area:
                areas.update(mapped_areas)
        
        # Also add the raw area
        areas.add(area.replace(' ', '_').replace('-', '_'))
    
    return areas


def _calculate_day_date(start_date: str, day_number: int) -> str:
    """Calculate the date for a given NTI day."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        target = start + timedelta(days=day_number - 1)
        return target.strftime('%A, %B %d, %Y')
    except ValueError:
        return f"Day {day_number}"


# ─────────────────────────────────────────────────────────────────────
# PARENT INSTRUCTIONS PAGE
# ─────────────────────────────────────────────────────────────────────

def _generate_parent_instructions(student: dict, category: str) -> str:
    """
    Generate the parent instruction page in simple, clear language.
    """
    first_name = student.get('first_name', 'your child')
    parent_name = student.get('parent_name', 'Parent/Guardian')
    comm_mode = student.get('communication_mode', 'verbal')
    
    # Communication mode tips
    comm_tips = {
        'verbal': f"Talk with {first_name} during activities. Ask simple questions and wait for answers.",
        'pecs': f"Use {first_name}'s picture communication book/board during activities. Help them point to or hand you pictures to make choices.",
        'device': f"Keep {first_name}'s communication device nearby during activities. Model using it to make requests and comments.",
        'gestures': f"Watch for {first_name}'s gestures and sounds during activities. Respond to any attempts to communicate — pointing, reaching, sounds all count!"
    }
    
    instructions = f"""
╔══════════════════════════════════════════════════════════════╗
║              NTI PACKET — PARENT INSTRUCTIONS               ║
╚══════════════════════════════════════════════════════════════╝

Dear {parent_name},

School is closed today, but learning continues at home!
Here are some activities for {first_name}. 

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW TO USE THIS PACKET:

  ✓ Pick 3-5 activities per day (you don't have to do ALL of them)
  ✓ Do activities when {first_name} is calm and happy
  ✓ Keep it short — 10-15 minutes per activity is great!
  ✓ Take breaks between activities
  ✓ It's okay to stop if {first_name} gets frustrated
  ✓ ANY attempt counts — we celebrate trying!
  ✓ Fill in the data sheet if you can (it helps us at school)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMMUNICATION TIPS:
  {comm_tips.get(comm_mode, comm_tips['verbal'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIPS FOR SUCCESS:

  • Do activities at a table or quiet area (less distractions)
  • Praise every attempt! ("Good trying!" "Nice work!")
  • If something is too hard, make it easier or skip it
  • Use items you already have at home — don't buy anything new
  • Your child might need hand-over-hand help — that's okay!
  • Have fun! Learning should feel good.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IF YOU HAVE QUESTIONS:
  Contact: [Teacher Name]
  Phone/Text: [Phone Number]
  Email: [Email Address]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLEASE RETURN this packet and data sheet when school resumes.
Thank you for being {first_name}'s learning partner! 💛

"""
    return instructions


# ─────────────────────────────────────────────────────────────────────
# DATA SHEET FOR PARENTS
# ─────────────────────────────────────────────────────────────────────

def _generate_data_sheet(days: list, student_name: str) -> str:
    """Generate a simple data sheet for parents to fill in."""
    sheet = f"""
╔══════════════════════════════════════════════════════════════╗
║              NTI DATA SHEET — Please Fill In                ║
╚══════════════════════════════════════════════════════════════╝

Student: {student_name}
Parent Signature: _________________________

"""
    
    for day in days:
        day_num = day['day_number']
        day_date = day['date']
        activities = day['activities']
        
        sheet += f"""
━━━ DAY {day_num}: {day_date} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, activity in enumerate(activities, 1):
            sheet += f"""  Activity {i}: {activity['title']}
    Did you do this activity?  □ Yes  □ No
    {activity.get('data_prompt', '')}

"""
        
        sheet += f"""  Overall, how did today go?
    □ Great day!   □ Okay   □ Tough day

  Notes/Questions for teacher:
  ________________________________________________________

"""
    
    sheet += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thank you for completing this! It really helps us at school.
Please send this back in your child's backpack.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return sheet


def _get_digital_suggestions(category: str) -> list:
    """Get digital activity suggestions for families with internet."""
    return DIGITAL_ACTIVITIES.get(category, [])


# ─────────────────────────────────────────────────────────────────────
# NTI COMPLIANCE TRACKING
# ─────────────────────────────────────────────────────────────────────

class NTIComplianceLog:
    """Track NTI packet generation and return for FAPE documentation."""
    
    def __init__(self):
        self._records = []
    
    def record_sent(self, student_id: str, student_name: str,
                    num_days: int, nti_date: str, method: str = 'printed'):
        """Record that an NTI packet was sent to a family."""
        record = {
            'id': len(self._records) + 1,
            'student_id': student_id,
            'student_name': student_name,
            'num_days': num_days,
            'nti_date': nti_date,
            'method': method,  # 'printed', 'emailed', 'hand_delivered'
            'sent_at': datetime.now().isoformat(),
            'returned': False,
            'returned_at': None,
            'data_sheet_completed': False,
            'notes': ''
        }
        self._records.append(record)
        return record
    
    def record_returned(self, record_id: int, data_sheet_completed: bool = False,
                        notes: str = ''):
        """Record that an NTI packet was returned."""
        for record in self._records:
            if record['id'] == record_id:
                record['returned'] = True
                record['returned_at'] = datetime.now().isoformat()
                record['data_sheet_completed'] = data_sheet_completed
                record['notes'] = notes
                return record
        return None
    
    def get_compliance_report(self, nti_date: str = None) -> dict:
        """Generate compliance report for a specific NTI date or all."""
        records = self._records
        if nti_date:
            records = [r for r in records if r['nti_date'] == nti_date]
        
        total = len(records)
        returned = sum(1 for r in records if r['returned'])
        
        return {
            'total_packets_sent': total,
            'packets_returned': returned,
            'return_rate': f"{(returned/total*100):.0f}%" if total > 0 else "N/A",
            'missing_returns': [
                r['student_name'] for r in records if not r['returned']
            ],
            'records': records
        }
    
    def get_student_history(self, student_id: str) -> list:
        """Get all NTI records for a specific student."""
        return [r for r in self._records if r['student_id'] == student_id]


# Module-level compliance log instance
nti_compliance = NTIComplianceLog()


# ─────────────────────────────────────────────────────────────────────
# PACKET FORMATTING (for display/printing)
# ─────────────────────────────────────────────────────────────────────

def format_packet_for_display(packet: dict) -> str:
    """
    Format a complete NTI packet as a printable text document.
    Used for preview and plain-text printing.
    """
    student = packet['student']
    first_name = student['first_name']
    
    output = packet['parent_instructions']
    output += "\n\n"
    
    for day in packet['days']:
        output += f"""
╔══════════════════════════════════════════════════════════════╗
║                    DAY {day['day_number']}: {day['date']:<36} ║
╚══════════════════════════════════════════════════════════════╝

Activities for {first_name}:
"""
        for i, activity in enumerate(day['activities'], 1):
            materials = ', '.join(activity.get('materials', ['None needed']))
            output += f"""
┌─────────────────────────────────────────────────────────────┐
│ Activity {i}: {activity['title']:<47} │
└─────────────────────────────────────────────────────────────┘

  WHAT TO DO:
  {activity['description']}

  YOU WILL NEED:
  {materials}

  HOW LONG:
  {activity.get('duration', '10-15 minutes')}

"""
            if activity.get('is_digital') and activity.get('url_suggestions'):
                output += "  WHERE TO FIND IT:\n"
                for url in activity['url_suggestions']:
                    output += f"    • {url}\n"
                output += "\n"
    
    output += packet['data_sheet']
    
    return output
