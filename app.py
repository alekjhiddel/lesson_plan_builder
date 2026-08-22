"""
SPARK
A privacy-first lesson plan generator for MSD/autism classrooms.
All student data stays local. Names are anonymized before any external AI interaction.
"""

import os
import sys
import json
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from modules.student_manager import (
    get_all_students, get_student, add_student, update_student, delete_student, ensure_data_dir
)
from modules.anonymizer import Anonymizer
from modules.prompt_builder import PromptBuilder
from modules.response_parser import ResponseParser
from modules.scraper import scrape_url, get_knowledge_base, delete_resource
from modules.scheduler import get_current_themes, get_scheduling_context, get_themes_for_month
from modules.api_mode import generate_with_api, is_api_configured
from modules.updater import check_for_updates, apply_update, get_current_version, export_backup_zip, restore_from_zip, list_backups
from modules.help_system import get_help_topic, get_all_help_topics, get_help_categories
from modules.iep_writer import IEPWriter
from modules.goal_bank import get_goals, get_all_domains, search_goals
from modules.data_collection import (
    add_data_point, get_goal_data, get_student_data_summary,
    calculate_progress, check_mastery, generate_data_sheet
)
from modules.progress_reports import generate_progress_report, generate_progress_prompt
from modules.parent_comms import generate_progress_letter, generate_daily_log
from modules.nti_generator import generate_nti_packet, generate_class_nti_packets
from modules.partner_sync import (
    export_for_partner, import_partner_students, get_partner_students,
    get_partner_classroom_summary, delete_partner_students
)
from modules.schedule_engine import (
    get_schedule_config, save_schedule_config, get_default_config,
    generate_schedule, format_schedule_for_display, format_schedule_for_prompt
)
from modules.break_activities import (
    get_all_activities, get_activities_by_category, get_categories,
    get_activities_for_student, get_random_break, format_break_for_display
)
from modules.manifestation_determination import (
    get_checklist, get_hb538_summary, evaluate_determination, get_timeline_info
)
from modules.sub_plans import generate_sub_plan, format_sub_plan_for_print
from modules.medical_safety import (
    get_medical_data, save_medical_data, generate_safety_sheet,
    get_all_medical_alerts, get_blank_medical_record
)
from modules.aide_training import generate_aide_packet, format_packet_for_print
from modules.visual_schedule import (
    get_saved_schedules, get_schedule, save_schedule, delete_schedule,
    get_default_schedule, get_available_icons, format_schedule_for_print as format_vs_for_print
)
from modules.related_services import (
    get_student_services, save_student_services, add_service, log_session,
    get_monthly_summary, get_dashboard_data, get_service_types, SERVICE_TYPES
)
from modules.esy_justification import (
    get_esy_candidates, generate_esy_justification, get_break_periods,
    save_break_periods, format_esy_report
)
from modules.goal_mastery import (
    check_all_mastery, get_mastery_criteria, set_mastery_criteria,
    get_suggested_next_goals, get_mastery_celebrations, mark_goal_mastered,
    get_mastered_goals_for_student
)
from modules.compliance_calendar import (
    get_compliance_dashboard, get_calendar_events, get_upcoming_deadlines,
    add_custom_event, remove_custom_event, get_all_custom_events
)
from modules.year_lifecycle import (
    get_current_year, set_current_year, is_migrated,
    get_teacher_stage, set_teacher_stage, get_stage_definitions
)
from modules.migration import needs_migration, migrate_to_year_aware


app = Flask(__name__)
app.secret_key = os.urandom(24)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
PLANS_DIR = os.path.join(DATA_DIR, 'lesson_plans')


def get_config():
    """Load app configuration."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'school_name': '',
            'teacher_name': '',
            'num_aides': 2,
            'has_floater': True,
            'api_key': '',
            'api_enabled': False,
            'setup_complete': False,
            'school_start_time': '8:00',
            'school_end_time': '2:35',
            'class_size': 9
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config):
    """Save app configuration."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def save_lesson_plan(plan_data):
    """Save a generated lesson plan to history."""
    os.makedirs(PLANS_DIR, exist_ok=True)
    from datetime import datetime
    filename = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(PLANS_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(plan_data, f, indent=2)
    return filename



# ============================================================
# AUTISM FAST FACTS DATA (Kentucky, source: KDE Dec 2024)
# ============================================================

def get_autism_fast_facts():
    """Return structured autism facts data for parent communications."""
    return {
        "title": "Kentucky Autism Fast Facts",
        "source": "Kentucky Department of Education, December 2024",
        "prevalence": {
            "national_rate": "1 in 36 children identified with ASD (CDC, 2023)",
            "ky_students_served": "Approximately 12,500 students ages 3-21 in Kentucky receive special education services under the autism eligibility category",
            "growth": "Kentucky has seen a 38% increase in autism identification over the past decade",
            "gender": "Boys are 4x more likely to be identified than girls"
        },
        "educational_data": {
            "placement": {
                "regular_class_80_plus": "42% of KY students with autism spend 80%+ of day in regular class",
                "regular_class_40_79": "18% spend 40-79% in regular class",
                "regular_class_under_40": "33% spend less than 40% in regular class",
                "separate_settings": "7% are in separate schools/residential/homebound"
            },
            "graduation": "Students with autism in KY graduate at approximately 72% rate (vs 90% general population)",
            "post_secondary": "About 36% of young adults with autism pursue post-secondary education"
        },
        "key_facts_for_parents": [
            "Autism is a neurological difference, not a disease — early intervention and quality education lead to best outcomes",
            "Every child with autism is unique — there is no single approach that works for all",
            "Kentucky law (IDEA & KRS 157) guarantees your child a Free Appropriate Public Education (FAPE)",
            "You are an equal member of your child's ARC/IEP team",
            "Your child's IEP must include measurable annual goals based on their present levels",
            "Visual supports, structured environments, and consistent routines are evidence-based practices",
            "Behavior is communication — challenging behavior often signals an unmet need",
            "Transition planning begins at age 14 in Kentucky (or earlier if appropriate)"
        ],
        "kentucky_resources": [
            {"name": "KY Commission on Autism Spectrum Disorders", "url": "https://autism.ky.gov"},
            {"name": "KDE Special Education", "url": "https://education.ky.gov/specialed"},
            {"name": "KY Autism Training Center (WKU)", "url": "https://www.wku.edu/katc/"},
            {"name": "First Steps (Early Intervention, birth-3)", "url": "https://chfs.ky.gov/agencies/dms/firststeps"},
        ]
    }

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def dashboard():
    config = get_config()
    if not config.get('setup_complete'):
        return redirect(url_for('setup_wizard'))
    if needs_migration():
        return redirect(url_for('migration_wizard'))
    students = get_all_students()
    themes = get_current_themes()
    return render_template('dashboard.html', 
                         students=students, 
                         themes=themes,
                         config=config,
                         student_count=len(students))


@app.route('/setup', methods=['GET', 'POST'])
def setup_wizard():
    if request.method == 'POST':
        config = get_config()
        config['teacher_name'] = request.form.get('teacher_name', '')
        config['school_name'] = request.form.get('school_name', '')
        config['num_aides'] = int(request.form.get('num_aides', 2))
        config['has_floater'] = request.form.get('has_floater') == 'yes'
        config['class_size'] = int(request.form.get('class_size', 9))
        config['school_start_time'] = request.form.get('school_start_time', '8:00')
        config['school_end_time'] = request.form.get('school_end_time', '2:35')
        config['setup_complete'] = True
        save_config(config)
        flash('Setup complete! Welcome aboard. 🎉', 'success')
        return redirect(url_for('dashboard'))
    return render_template('setup_wizard.html')


# --- Migration Route ---

@app.route('/migrate', methods=['GET', 'POST'])
def migration_wizard():
    """One-time migration wizard for year-over-year tracking."""
    if not needs_migration():
        # Already migrated — go to dashboard
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        current_year = request.form.get('current_year', '2026-27').strip()
        stage_key = request.form.get('stage', 'elementary')
        
        try:
            # Run the migration
            report = migrate_to_year_aware(year=current_year, stage_key=stage_key)
            
            # Set the teacher stage
            set_teacher_stage(stage_key)
            
            migrated_count = report.get('students_migrated', 0) if report else 0
            if migrated_count > 0:
                flash(f'Year tracking enabled! {migrated_count} student{"s" if migrated_count != 1 else ""} migrated to {current_year}. 🎉', 'success')
            else:
                flash(f'Year tracking enabled for {current_year}! Add students to get started. 🎉', 'success')
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Migration error: {str(e)}. Your data is safe — try again.', 'error')
            return redirect(url_for('migration_wizard'))
    
    # GET — show the wizard
    students = get_all_students()
    return render_template('migration_wizard.html',
                         student_count=len(students),
                         current_year='2026-27')


# --- Student Routes ---

@app.route('/students')
def students_list():
    students = get_all_students()
    return render_template('students.html', students=students)


@app.route('/students/add', methods=['GET', 'POST'])
def student_add():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', ''),
            'age': request.form.get('age', ''),
            'grade': request.form.get('grade', ''),
            'iep_goals': [g.strip() for g in request.form.get('iep_goals', '').split('\n\n') if g.strip()],
            'iep_annual_review_date': request.form.get('iep_annual_review_date', ''),
            'related_services': request.form.get('related_services', ''),
            'sdi_notes': request.form.get('sdi_notes', ''),
            'physical_needs': [n.strip() for n in request.form.get('physical_needs', '').split('\n\n') if n.strip()],
            'cognitive_needs': request.form.get('cognitive_needs', ''),
            'behavioral_needs': request.form.get('behavioral_needs', ''),
            'sensory_needs': request.form.get('sensory_needs', ''),
            'communication_mode': request.form.get('communication_mode', ''),
            'communication_details': request.form.get('communication_details', ''),
            'homeroom_attends': request.form.get('homeroom_attends') == 'yes',
            'homeroom_duration': request.form.get('homeroom_duration', ''),
            'homeroom_aide_accompanies': request.form.get('homeroom_aide_accompanies') == 'yes',
            'homeroom_schedule': request.form.get('homeroom_schedule', ''),
            'focus_areas': [a.strip() for a in request.form.get('focus_areas', '').split('\n\n') if a.strip()],
            'reinforcers': request.form.get('reinforcers', ''),
            'life_skills_priorities': [l.strip() for l in request.form.get('life_skills_priorities', '').split('\n\n') if l.strip()],
            'notes': request.form.get('notes', '')
        }
        add_student(data)
        flash(f'{data["name"]} has been added! ✨', 'success')
        return redirect(url_for('students_list'))
    return render_template('student_form.html', student=None, action='Add')


@app.route('/students/edit/<student_id>', methods=['GET', 'POST'])
def student_edit(student_id):
    student = get_student(student_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('students_list'))
    
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', ''),
            'age': request.form.get('age', ''),
            'grade': request.form.get('grade', ''),
            'iep_goals': [g.strip() for g in request.form.get('iep_goals', '').split('\n\n') if g.strip()],
            'iep_annual_review_date': request.form.get('iep_annual_review_date', ''),
            'related_services': request.form.get('related_services', ''),
            'sdi_notes': request.form.get('sdi_notes', ''),
            'physical_needs': [n.strip() for n in request.form.get('physical_needs', '').split('\n\n') if n.strip()],
            'cognitive_needs': request.form.get('cognitive_needs', ''),
            'behavioral_needs': request.form.get('behavioral_needs', ''),
            'sensory_needs': request.form.get('sensory_needs', ''),
            'communication_mode': request.form.get('communication_mode', ''),
            'communication_details': request.form.get('communication_details', ''),
            'homeroom_attends': request.form.get('homeroom_attends') == 'yes',
            'homeroom_duration': request.form.get('homeroom_duration', ''),
            'homeroom_aide_accompanies': request.form.get('homeroom_aide_accompanies') == 'yes',
            'homeroom_schedule': request.form.get('homeroom_schedule', ''),
            'focus_areas': [a.strip() for a in request.form.get('focus_areas', '').split('\n\n') if a.strip()],
            'reinforcers': request.form.get('reinforcers', ''),
            'life_skills_priorities': [l.strip() for l in request.form.get('life_skills_priorities', '').split('\n\n') if l.strip()],
            'notes': request.form.get('notes', '')
        }
        update_student(student_id, data)
        flash(f'{data["name"]}\'s profile has been updated! ✅', 'success')
        return redirect(url_for('students_list'))
    return render_template('student_form.html', student=student, action='Edit')


@app.route('/students/delete/<student_id>', methods=['POST'])
def student_delete(student_id):
    student = get_student(student_id)
    name = student['name'] if student else 'Student'
    delete_student(student_id)
    flash(f'{name} has been removed.', 'info')
    return redirect(url_for('students_list'))


# --- Plan Generation Routes ---

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    students = get_all_students()
    config = get_config()
    themes = get_current_themes()
    
    if request.method == 'POST':
        plan_type = request.form.get('plan_type', 'weekly')
        selected_month = int(request.form.get('month', 0))
        custom_theme = request.form.get('custom_theme', '')
        additional_notes = request.form.get('additional_notes', '')
        
        para_notes_style = request.form.get('para_notes_style', 'detailed')
        
        builder = PromptBuilder()
        prompt = builder.build_prompt(
            students=students,
            config=config,
            plan_type=plan_type,
            month_override=selected_month if selected_month else None,
            custom_theme=custom_theme,
            additional_notes=additional_notes,
            para_notes_style=para_notes_style
        )
        
        if config.get('api_enabled') and is_api_configured(config):
            # Direct API mode
            response = generate_with_api(prompt, config)
            if response:
                parser = ResponseParser()
                processed = parser.process_response(response, students)
                save_lesson_plan({
                    'type': plan_type,
                    'prompt': prompt,
                    'raw_response': response,
                    'processed': processed,
                    'generated_at': __import__('datetime').datetime.now().isoformat()
                })
                return render_template('result.html', 
                                     plan=processed, 
                                     plan_type=plan_type,
                                     raw_response=response)
            else:
                flash('API call failed. Try copy/paste mode instead.', 'error')
        
        # Copy/paste mode - show the prompt
        return render_template('prompt_display.html', 
                             prompt=prompt, 
                             plan_type=plan_type)
    
    return render_template('generate.html', 
                         students=students, 
                         themes=themes,
                         config=config)


@app.route('/process', methods=['GET', 'POST'])
def process_response():
    students = get_all_students()
    
    if request.method == 'POST':
        raw_response = request.form.get('response_text', '')
        plan_type = request.form.get('plan_type', 'weekly')
        
        if raw_response.strip():
            parser = ResponseParser()
            processed = parser.process_response(raw_response, students)
            save_lesson_plan({
                'type': plan_type,
                'raw_response': raw_response,
                'processed': processed,
                'generated_at': __import__('datetime').datetime.now().isoformat()
            })
            flash('Lesson plan processed and saved! 📋', 'success')
            return render_template('result.html', 
                                 plan=processed, 
                                 plan_type=plan_type,
                                 raw_response=raw_response)
        else:
            flash('Please paste the ChatGPT response first.', 'error')
    
    return render_template('process.html', students=students)


# --- Knowledge Base Routes ---

@app.route('/knowledge-base')
def knowledge_base():
    resources = get_knowledge_base()
    return render_template('knowledge_base.html', resources=resources)


@app.route('/knowledge-base/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'error': 'Please enter a URL'})
    
    result = scrape_url(url)
    if result['success']:
        return jsonify({'success': True, 'message': f'Successfully saved: {result["title"]}'})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to scrape URL')})


@app.route('/knowledge-base/delete/<resource_id>', methods=['POST'])
def delete_kb_resource(resource_id):
    delete_resource(resource_id)
    flash('Resource removed.', 'info')
    return redirect(url_for('knowledge_base'))


# --- History Routes ---

@app.route('/history')
def history():
    os.makedirs(PLANS_DIR, exist_ok=True)
    plans = []
    for filename in sorted(os.listdir(PLANS_DIR), reverse=True):
        if filename.endswith('.json'):
            filepath = os.path.join(PLANS_DIR, filename)
            with open(filepath, 'r') as f:
                plan = json.load(f)
                plan['filename'] = filename
                plans.append(plan)
    return render_template('history.html', plans=plans)


@app.route('/history/<filename>')
def view_plan(filename):
    filepath = os.path.join(PLANS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            plan = json.load(f)
        return render_template('result.html', 
                             plan=plan.get('processed', plan.get('raw_response', '')),
                             plan_type=plan.get('type', 'weekly'),
                             raw_response=plan.get('raw_response', ''))
    flash('Plan not found.', 'error')
    return redirect(url_for('history'))


# --- Schedule Routes ---

@app.route('/schedule')
def schedule():
    students = get_all_students()
    schedule_config = get_schedule_config()
    
    # Count homeroom students
    homeroom_count = sum(1 for s in students if s.get('homeroom_attends'))
    
    # Check if we have a generated schedule
    generated = None
    schedule_html_content = ''
    schedule_file = os.path.join(DATA_DIR, 'current_schedule.json')
    if os.path.exists(schedule_file):
        with open(schedule_file, 'r') as f:
            generated = json.load(f)
            schedule_html_content = format_schedule_for_display(generated)
    
    return render_template('schedule.html',
                         schedule_config=schedule_config,
                         homeroom_count=homeroom_count,
                         schedule=generated,
                         schedule_html=schedule_html_content)


@app.route('/schedule/setup', methods=['GET', 'POST'])
def schedule_setup():
    config = get_schedule_config()
    
    if request.method == 'POST':
        config['num_dedicated_aides'] = int(request.form.get('num_dedicated_aides') or 2)
        config['aide_names'] = request.form.getlist('aide_names')
        # Ensure we have enough aide names
        while len(config['aide_names']) < config['num_dedicated_aides']:
            config['aide_names'].append(f"Aide {len(config['aide_names']) + 1}")
        config['aide_names'] = config['aide_names'][:config['num_dedicated_aides']]
        
        config['has_floater'] = request.form.get('has_floater') == 'yes'
        config['floater_name'] = request.form.get('floater_name', 'Floater')
        config['min_aides_in_own_room'] = int(request.form.get('min_aides_in_own_room') or 1)
        config['min_aides_in_partner_room'] = 1  # Hard rule: always 1 aide in partner room
        
        config['partner_teacher'] = {
            'enabled': request.form.get('partner_enabled') == 'yes',
            'name': request.form.get('partner_name', ''),
            'num_aides': int(request.form.get('partner_num_aides') or 2),
            'aide_names': [f"Partner Aide {i+1}" for i in range(int(request.form.get('partner_num_aides') or 2))],
            'num_students': int(request.form.get('partner_num_students') or 0),
            'shared_floater': request.form.get('shared_floater') == 'yes',
            'notes': request.form.get('partner_notes', '')
        }
        
        config['configured'] = True
        save_schedule_config(config)
        
        # Auto-generate schedule
        students = get_all_students()
        if students:
            try:
                generated = generate_schedule(students, config)
                schedule_file = os.path.join(DATA_DIR, 'current_schedule.json')
                with open(schedule_file, 'w') as f:
                    json.dump(generated, f, indent=2, default=str)
                flash('Staffing saved and schedule generated! 📅', 'success')
            except Exception as e:
                flash(f'Staffing saved, but schedule generation failed: {str(e)}. Try adding more student details.', 'error')
        else:
            flash('Staffing saved! Add students to generate a schedule.', 'success')
        
        return redirect(url_for('schedule'))
    
    return render_template('schedule_setup.html', config=config)


@app.route('/schedule/generate', methods=['POST'])
def generate_schedule_route():
    students = get_all_students()
    config = get_schedule_config()
    
    if not students:
        flash('Add students first before generating a schedule.', 'error')
        return redirect(url_for('schedule'))
    
    try:
        generated = generate_schedule(students, config)
        schedule_file = os.path.join(DATA_DIR, 'current_schedule.json')
        with open(schedule_file, 'w') as f:
            json.dump(generated, f, indent=2, default=str)
        flash('Schedule regenerated! ✅', 'success')
    except Exception as e:
        flash(f'Schedule generation failed: {str(e)}. Check staffing setup and student details.', 'error')

    return redirect(url_for('schedule'))


# --- Settings Routes ---

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    config = get_config()
    if request.method == 'POST':
        config['teacher_name'] = request.form.get('teacher_name', config['teacher_name'])
        config['school_name'] = request.form.get('school_name', config['school_name'])
        config['num_aides'] = int(request.form.get('num_aides', config['num_aides']))
        config['has_floater'] = request.form.get('has_floater') == 'yes'
        config['class_size'] = int(request.form.get('class_size', config['class_size']))
        config['school_start_time'] = request.form.get('school_start_time', config['school_start_time'])
        config['school_end_time'] = request.form.get('school_end_time', config['school_end_time'])
        config['api_key'] = request.form.get('api_key', config.get('api_key', ''))
        config['api_enabled'] = request.form.get('api_enabled') == 'yes'
        save_config(config)
        flash('Settings saved! ⚙️', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html', config=config, update_result=None)


# --- Update Routes ---

@app.route('/check-updates')
def check_updates():
    result = check_for_updates()
    return jsonify(result)


# --- ESY Justification Routes ---

@app.route('/esy')
def esy_page():
    """ESY justification dashboard."""
    students = get_all_students()
    candidates = get_esy_candidates(students, get_goal_data)
    return render_template('esy.html',
                         students=students,
                         candidates=candidates,
                         justification=None)


@app.route('/esy/generate', methods=['POST'])
def esy_generate():
    """Generate ESY justification for a student."""
    student_id = request.form.get('student_id', '')
    students = get_all_students()
    student = get_student(student_id) if student_id else None
    
    if not student:
        flash('Student not found.')
        return redirect(url_for('esy_page'))
    
    candidates = get_esy_candidates([student], get_goal_data)
    if candidates:
        regressions = candidates[0].get('regressions', [])
        justification = generate_esy_justification(student, regressions)
    else:
        justification = {
            'student_name': student.get('name', ''),
            'generated_date': '',
            'narrative': 'No regression data found for this student.',
            'goal_details': [],
            'recommendation': 'Insufficient evidence for ESY',
        }
    
    return render_template('esy.html',
                         students=students,
                         candidates=[],
                         justification=justification)


@app.route('/esy/settings', methods=['GET', 'POST'])
def esy_settings_page():
    """Configure break periods for ESY tracking."""
    saved = False
    if request.method == 'POST':
        periods = get_break_periods()
        for period in periods:
            pid = period['id']
            period['start'] = request.form.get('start_' + pid, period['start'])
            period['end'] = request.form.get('end_' + pid, period['end'])
            period['data_window_before_days'] = int(request.form.get('before_' + pid, period['data_window_before_days']))
            period['data_window_after_days'] = int(request.form.get('after_' + pid, period['data_window_after_days']))
        save_break_periods(periods)
        saved = True
    
    break_periods = get_break_periods()
    return render_template('esy_settings.html', break_periods=break_periods, saved=saved)


# --- Goal Mastery Routes ---

@app.route('/mastery')
def mastery_page():
    """Goal mastery dashboard."""
    students = get_all_students()
    mastery_check = check_all_mastery(students, get_goal_data)
    celebrations = get_mastery_celebrations()
    
    # Build criteria map for display
    criteria_map = {}
    for student in students:
        sid = student.get('id', '')
        criteria_map[sid] = get_mastery_criteria(sid, '_default')
    
    return render_template('goal_mastery.html',
                         students=students,
                         mastery_check=mastery_check,
                         celebrations=celebrations,
                         criteria_map=criteria_map,
                         suggestions=None,
                         confirmed_student_name=None,
                         criteria_saved=False)


@app.route('/mastery/mark', methods=['POST'])
def mastery_mark():
    """Confirm a goal as mastered and show suggestions."""
    from modules.goal_bank import GOAL_BANK
    
    student_id = request.form.get('student_id', '')
    student_name = request.form.get('student_name', '')
    goal_id = request.form.get('goal_id', '')
    goal_text = request.form.get('goal_text', '')
    
    mark_goal_mastered(student_id, student_name, goal_id, goal_text)
    suggestions = get_suggested_next_goals(goal_id, GOAL_BANK)
    
    students = get_all_students()
    mastery_check = check_all_mastery(students, get_goal_data)
    celebrations = get_mastery_celebrations()
    criteria_map = {}
    for student in students:
        sid = student.get('id', '')
        criteria_map[sid] = get_mastery_criteria(sid, '_default')
    
    return render_template('goal_mastery.html',
                         students=students,
                         mastery_check=mastery_check,
                         celebrations=celebrations,
                         criteria_map=criteria_map,
                         suggestions=suggestions,
                         confirmed_student_name=student_name,
                         criteria_saved=False)


@app.route('/mastery/criteria', methods=['POST'])
def mastery_criteria_save():
    """Save mastery criteria for students."""
    students = get_all_students()
    for student in students:
        sid = student.get('id', '')
        threshold = request.form.get('threshold_' + sid, '80')
        consecutive = request.form.get('consecutive_' + sid, '3')
        set_mastery_criteria(sid, '_default', int(threshold), int(consecutive))
    
    mastery_check = check_all_mastery(students, get_goal_data)
    celebrations = get_mastery_celebrations()
    criteria_map = {}
    for student in students:
        sid = student.get('id', '')
        criteria_map[sid] = get_mastery_criteria(sid, '_default')
    
    return render_template('goal_mastery.html',
                         students=students,
                         mastery_check=mastery_check,
                         celebrations=celebrations,
                         criteria_map=criteria_map,
                         suggestions=None,
                         confirmed_student_name=None,
                         criteria_saved=True)


@app.route('/check-updates-page')
def check_updates_page():
    """Check for updates and render settings page with result (no JS needed)."""
    config = get_config()
    result = check_for_updates()
    return render_template('settings.html', config=config, update_result=result)


@app.route('/apply-update', methods=['POST'])
def do_update():
    result = apply_update()
    if result.get('success'):
        config = get_config()
        return render_template('settings.html', config=config, 
                             update_result={'available': False, 'message': result['message'] + ' Click Restart below.'},
                             show_restart=True)
    config = get_config()
    return render_template('settings.html', config=config, update_result={'error': result.get('error', 'Update failed')})


@app.route('/restart', methods=['POST'])
def restart_app():
    """Restart the Flask app after an update."""
    import subprocess
    # Start a new instance of the app, then exit this one
    script_path = os.path.join(APP_DIR, 'start.command')
    subprocess.Popen(['bash', script_path], start_new_session=True)
    # Give the response time to send before we exit
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    else:
        os._exit(0)
    return 'Restarting...'


# --- IEP Routes ---

@app.route('/iep')
def iep():
    students = get_all_students()
    domains = get_all_domains()
    return render_template('iep.html' if os.path.exists(os.path.join(app.template_folder, 'iep.html')) else 'dashboard.html',
                         students=students, domains=domains)


@app.route('/iep/goals')
def iep_goals():
    domain = request.args.get('domain', '')
    goals = get_goals(domain) if domain else {}
    domains = get_all_domains()
    return render_template('iep_goals.html' if os.path.exists(os.path.join(app.template_folder, 'iep_goals.html')) else 'generate.html',
                         goals=goals, domains=domains, selected_domain=domain)


@app.route('/iep/goals/search')
def iep_goals_search():
    query = request.args.get('q', '')
    results = search_goals(query) if query else []
    return jsonify({'results': results})


@app.route('/iep/generate', methods=['POST'])
def iep_generate():
    students = get_all_students()
    student_id = request.form.get('student_id', '')
    iep_type = request.form.get('iep_type', 'full')
    
    student = get_student(student_id) if student_id else None
    if not student:
        flash('Please select a student.', 'error')
        return redirect(url_for('iep'))
    
    config = get_config()
    writer = IEPWriter()
    prompt = writer.generate_iep_prompt(student, config, iep_type)
    
    return render_template('prompt_display.html', prompt=prompt, plan_type='iep')


@app.route('/iep/arc-prep', methods=['GET', 'POST'])
def iep_arc_prep():
    students = get_all_students()
    if request.method == 'POST':
        student_id = request.form.get('student_id', '')
        student = get_student(student_id) if student_id else None
        if student:
            config = get_config()
            writer = IEPWriter()
            prompt = writer.generate_arc_prep_prompt(student, config)
            return render_template('prompt_display.html', prompt=prompt, plan_type='arc_prep')
        flash('Please select a student.', 'error')
    return render_template('iep_arc_prep.html' if os.path.exists(os.path.join(app.template_folder, 'iep_arc_prep.html')) else 'generate.html',
                         students=students)


# --- Data & Progress Routes ---

@app.route('/data/entry', methods=['GET', 'POST'])
def data_entry():
    students = get_all_students()
    if request.method == 'POST':
        student_id = request.form.get('student_id', '')
        goal_text = request.form.get('goal_text', '')
        value = request.form.get('value', '')
        method = request.form.get('method', 'trial')
        notes = request.form.get('notes', '')
        behavior_category = request.form.get('behavior_category', '')
        
        if student_id and goal_text and value:
            from datetime import date
            add_data_point(student_id, goal_text, date.today().isoformat(), value, method, notes, behavior_category)
            flash('Data saved! ✅', 'success')
        else:
            flash('Please fill in all required fields.', 'error')
    
    return render_template('data_entry.html', students=students)


@app.route('/data/sheets')
def data_sheets():
    students = get_all_students()
    return render_template('data_sheets.html', students=students)


@app.route('/data/progress-report', methods=['GET', 'POST'])
def data_progress_report():
    students = get_all_students()
    if request.method == 'POST':
        student_id = request.form.get('student_id', '')
        student = get_student(student_id) if student_id else None
        if student:
            config = get_config()
            prompt = generate_progress_prompt(student, [])
            return render_template('prompt_display.html', prompt=prompt, plan_type='progress_report')
        flash('Please select a student.', 'error')
    return render_template('progress_report_view.html', students=students)


@app.route('/data/graphs')
def data_graphs():
    students = get_all_students()
    student_id = request.args.get('student_id', '')
    student_data = None
    if student_id:
        student_data = get_student_data_summary(student_id)
    return render_template('progress_graphs.html', students=students, student_data=student_data)


# --- Parent Communications Routes ---

@app.route('/communications')
def communications():
    students = get_all_students()
    return render_template('parent_comms.html', students=students)


@app.route('/communications/daily-log', methods=['GET', 'POST'])
def daily_log():
    students = get_all_students()
    if request.method == 'POST':
        student_id = request.form.get('student_id', '')
        day_rating = request.form.get('day_rating', 'good')
        activities = request.form.get('activities', '')
        notes = request.form.get('notes', '')
        
        student = get_student(student_id) if student_id else None
        if student:
            log = generate_daily_log(student, request.form.get('date', ''), activities or [], day_rating, notes)
            return render_template('daily_log.html', students=students, log=log, generated=True)
    
    return render_template('daily_log.html', students=students, generated=False)


@app.route('/communications/generate', methods=['POST'])
def comms_generate():
    students = get_all_students()
    student_id = request.form.get('student_id', '')
    comm_type = request.form.get('comm_type', 'progress_letter')
    
    student = get_student(student_id) if student_id else None
    if not student:
        flash('Please select a student.', 'error')
        return redirect(url_for('communications'))
    
    config = get_config()
    prompt = generate_progress_letter(student, comm_type, tone='professional')
    
    return render_template('prompt_display.html', prompt=prompt, plan_type=comm_type)


# --- NTI Routes ---

@app.route('/nti')
def nti():
    students = get_all_students()
    config = get_config()
    return render_template('nti.html', students=students, config=config)


@app.route('/nti/generate', methods=['POST'])
def nti_generate():
    students = get_all_students()
    num_days = int(request.form.get('num_days', 1))
    selected_ids = request.form.getlist('student_ids')
    
    if not selected_ids:
        selected_ids = [s['id'] for s in students]
    
    selected_students = [s for s in students if s['id'] in selected_ids]
    config = get_config()
    
    prompt = generate_class_nti_packets(selected_students, num_days)
    
    return render_template('prompt_display.html', prompt=prompt, plan_type='nti')


# --- Help Routes ---

@app.route('/help')
def help_index():
    categories = get_help_categories()
    return render_template('help.html', categories=categories)


@app.route('/help/<topic_id>')
def help_topic(topic_id):
    topic = get_help_topic(topic_id)
    return render_template('help_topic.html', topic=topic, topic_id=topic_id)


# --- Partner Teacher Routes ---

@app.route('/partner')
def partner():
    partner_summary = get_partner_classroom_summary()
    return render_template('partner.html', partners=partner_summary)


@app.route('/partner/export')
def partner_export():
    students = get_all_students()
    config = get_config()
    export_text = export_for_partner(students, config)
    return render_template('partner_export.html', export_text=export_text)


@app.route('/partner/import', methods=['GET', 'POST'])
def partner_import():
    if request.method == 'POST':
        import_text = request.form.get('import_text', '').strip()
        if not import_text:
            flash('Please paste the partner export data.', 'error')
            return render_template('partner_import.html')
        
        result = import_partner_students(import_text)
        if result['success']:
            flash(f"✅ {result['message']}", 'success')
            return redirect(url_for('partner'))
        else:
            flash(f"❌ {result['error']}", 'error')
    
    return render_template('partner_import.html')


@app.route('/partner/delete/<partner_name>', methods=['POST'])
def partner_delete(partner_name):
    delete_partner_students(partner_name)
    flash(f'Removed {partner_name}\'s student data.', 'info')
    return redirect(url_for('partner'))


# --- Backup Routes ---

@app.route('/backup/export')
def export_backup():
    result = export_backup_zip()
    if result['success']:
        return send_file(
            result['path'],
            as_attachment=True,
            download_name=result['filename']
        )
    return jsonify(result)


@app.route('/backup/restore', methods=['POST'])
def restore_backup():
    if 'backup_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['backup_file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    # Save uploaded file to temp location
    import tempfile
    temp_path = os.path.join(tempfile.gettempdir(), 'spark_restore.zip')
    file.save(temp_path)
    
    result = restore_from_zip(temp_path)
    os.remove(temp_path)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['error'], 'error')
    
    return redirect(url_for('settings'))


# ============================================================
# MAIN
# ============================================================


# --- Break/Regulation Activity Bank Routes ---

@app.route('/breaks')
def breaks():
    activities = get_all_activities()
    categories = get_categories()
    return render_template('breaks.html', activities=activities, categories=categories)


@app.route('/breaks/random')
def break_random():
    category = request.args.get('category', None)
    duration = int(request.args.get('duration', 5))
    comm_mode = request.args.get('mode', None)
    activity = get_random_break(category=category, duration_max=duration, comm_mode=comm_mode)
    if activity:
        return jsonify(format_break_for_display(activity))
    return jsonify({'error': 'No matching activities'}), 404


# --- Manifestation Determination Routes ---

@app.route('/manifestation')
def manifestation():
    students = get_all_students()
    checklist = get_checklist()
    hb538 = get_hb538_summary()
    return render_template('manifestation.html', 
                         students=students, checklist=checklist, hb538=hb538)


@app.route('/manifestation/evaluate', methods=['POST'])
def manifestation_evaluate():
    det_1 = request.form.get('det_1') == 'yes'
    det_2 = request.form.get('det_2') == 'yes'
    result = evaluate_determination(det_1, det_2)
    return jsonify(result)


# --- Autism Fast Facts Resource Route ---

@app.route('/resources/autism-facts')
def autism_fast_facts():
    """Display Kentucky Autism Fast Facts as a parent-shareable resource."""
    facts = get_autism_fast_facts()
    return render_template('autism_facts.html', facts=facts)


# --- Lesson Plan Repeat Route ---

@app.route('/generate/repeat-last', methods=['GET', 'POST'])
def repeat_last_plan():
    """Copy last week's plan structure forward with option to change theme/materials."""
    import glob
    
    # Find the most recent plan
    os.makedirs(PLANS_DIR, exist_ok=True)
    plan_files = sorted(glob.glob(os.path.join(PLANS_DIR, 'plan_*.json')), reverse=True)
    
    last_plan = None
    if plan_files:
        with open(plan_files[0], 'r') as f:
            last_plan = json.load(f)
    
    if request.method == 'POST' and last_plan:
        # User confirmed repeat with new theme
        new_theme = request.form.get('new_theme', '')
        new_notes = request.form.get('new_notes', '')
        
        config = get_config()
        students = get_all_students()
        builder = PromptBuilder()
        
        # Build prompt with "repeat structure" instruction
        repeat_instruction = (
            "IMPORTANT: Repeat the same activity structure and schedule as last week. "
            "MSD students thrive on routine — keep the same flow. "
            "Only update the theme/materials as noted below. "
            "Keep the same centers, same transitions, same aide assignments."
        )
        if new_theme:
            repeat_instruction += f"\nNew theme this week: {new_theme}"
        if new_notes:
            repeat_instruction += f"\nChanges from last week: {new_notes}"
        
        prompt = builder.build_prompt(
            students=students,
            config=config,
            plan_type='weekly',
            additional_notes=repeat_instruction
        )
        
        if config.get('api_enabled') and is_api_configured(config):
            response = generate_with_api(prompt, config)
            if response:
                parser = ResponseParser()
                processed = parser.process_response(response, students)
                save_lesson_plan({
                    'type': 'weekly_repeat',
                    'prompt': prompt,
                    'raw_response': response,
                    'processed': processed,
                    'generated_at': __import__('datetime').datetime.now().isoformat(),
                    'repeated_from': plan_files[0]
                })
                return render_template('result.html', plan=processed, 
                                     plan_type='weekly', raw_response=response)
        
        # Copy/paste mode
        return render_template('prompt_display.html', prompt=prompt, plan_type='weekly_repeat')
    
    return render_template('repeat_plan.html', last_plan=last_plan)


def open_browser():
    """Open browser after a short delay to let the server start."""
    import time
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')


# ============================================================
# SUB PLANS ROUTES
# ============================================================

@app.route('/sub-plans')
def sub_plans():
    return render_template('sub_plans.html', plan=None)


@app.route('/sub-plans/generate', methods=['POST'])
def generate_sub_plan_route():
    students = get_all_students()
    config = get_config()
    plan = generate_sub_plan(students, config)
    return render_template('sub_plans.html', plan=plan)


# ============================================================
# MEDICAL/SAFETY ROUTES
# ============================================================

@app.route('/medical')
def medical_safety():
    students = get_all_students()
    alerts = get_all_medical_alerts(students)
    return render_template('medical_safety.html', students=students, alerts=alerts)


@app.route('/medical/edit/<student_id>', methods=['GET', 'POST'])
def edit_medical(student_id):
    if request.method == 'POST':
        data = {
            "allergies": request.form.get("allergies", ""),
            "medications": json.loads(request.form.get("medications_json", "[]")),
            "seizure_protocol": {
                "has_seizures": request.form.get("has_seizures") == "yes",
                "type": request.form.get("seizure_type", ""),
                "protocol": request.form.get("seizure_protocol", ""),
                "rescue_med": request.form.get("rescue_med", ""),
                "rescue_med_location": request.form.get("rescue_med_location", ""),
            },
            "elopement_risk": {
                "is_risk": request.form.get("elopement_risk") == "yes",
                "protocol": request.form.get("elopement_protocol", ""),
                "triggers": request.form.get("elopement_triggers", ""),
            },
            "emergency_contacts": [
                {"name": request.form.get("contact1_name", ""), "relationship": request.form.get("contact1_rel", ""), "phone": request.form.get("contact1_phone", ""), "is_primary": True},
                {"name": request.form.get("contact2_name", ""), "relationship": request.form.get("contact2_rel", ""), "phone": request.form.get("contact2_phone", ""), "is_primary": False},
            ],
            "hospital_preference": request.form.get("hospital", ""),
            "doctor_name": request.form.get("doctor_name", ""),
            "doctor_phone": request.form.get("doctor_phone", ""),
            "dietary_restrictions": request.form.get("dietary", ""),
            "sensory_triggers": request.form.get("sensory_triggers", ""),
            "physical_limitations": request.form.get("physical", ""),
            "toileting_needs": request.form.get("toileting", ""),
            "additional_notes": request.form.get("notes", ""),
        }
        save_medical_data(student_id, data)
        flash("Medical information saved!", "success")
        return redirect(url_for('medical_safety'))
    
    student = get_student(student_id)
    medical_data = get_medical_data(student_id)
    return render_template('medical_edit.html', student=student, medical=medical_data)


@app.route('/medical/print/<student_id>')
def print_safety_sheet(student_id):
    student = get_student(student_id)
    medical_data = get_medical_data(student_id)
    sheet = generate_safety_sheet(student, medical_data)
    return render_template('safety_sheet_print.html', sheet=sheet)


# ============================================================
# AIDE TRAINING ROUTES
# ============================================================

@app.route('/aide-training')
def aide_training():
    return render_template('aide_training.html', packet=None)


@app.route('/aide-training/generate', methods=['POST'])
def generate_aide_packet_route():
    students = get_all_students()
    config = get_config()
    packet = generate_aide_packet(students, config)
    return render_template('aide_training.html', packet=packet)


# ============================================================
# VISUAL SCHEDULE ROUTES
# ============================================================

@app.route('/visual-schedules')
def visual_schedules():
    saved = get_saved_schedules()
    default = get_default_schedule()
    icons = get_available_icons()
    return render_template('visual_schedule.html', saved_schedules=saved, default_schedule=default, icons=icons)


@app.route('/visual-schedules/save', methods=['POST'])
def save_visual_schedule():
    name = request.form.get('name', 'Untitled Schedule')
    schedule_type = request.form.get('type', 'class')
    
    activities = []
    names = request.form.getlist('activity_name[]')
    durations = request.form.getlist('activity_duration[]')
    transitions = request.form.getlist('activity_transition[]')
    icons = request.form.getlist('activity_icon[]')
    
    for i in range(len(names)):
        if names[i].strip():
            activities.append({
                "activity": names[i].strip(),
                "duration": int(durations[i]) if i < len(durations) and durations[i] else 15,
                "transition_cue": transitions[i].strip() if i < len(transitions) else "",
                "icon": icons[i] if i < len(icons) else "transition",
            })
    
    save_schedule(name, activities, schedule_type)
    flash(f"Schedule \'{name}\' saved!", "success")
    return redirect(url_for('visual_schedules'))


@app.route('/visual-schedules/print/<filename>')
def print_visual_schedule(filename):
    schedule = get_schedule(filename)
    if not schedule:
        flash("Schedule not found", "error")
        return redirect(url_for('visual_schedules'))
    icons = get_available_icons()
    formatted = format_vs_for_print(schedule)
    return render_template('visual_schedule_print.html', schedule=schedule, formatted=formatted, icons=icons)


@app.route('/visual-schedules/delete/<filename>')
def delete_visual_schedule(filename):
    delete_schedule(filename)
    flash("Schedule deleted", "success")
    return redirect(url_for('visual_schedules'))


# ============================================================
# RELATED SERVICES ROUTES
# ============================================================

@app.route('/services')
def services_dashboard():
    students = get_all_students()
    dashboard = get_dashboard_data(students)
    return render_template('services_dashboard.html', dashboard=dashboard)


@app.route('/services/add', methods=['GET', 'POST'])
def add_service_page():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        add_service(
            student_id=student_id,
            service_type=request.form.get('service_type', ''),
            provider_name=request.form.get('provider', ''),
            frequency=request.form.get('frequency', ''),
            minutes_per_session=int(request.form.get('minutes', 30)),
            notes=request.form.get('notes', ''),
        )
        flash("Service added!", "success")
        return redirect(url_for('services_dashboard'))
    
    students = get_all_students()
    return render_template('services_add.html', students=students, service_types=SERVICE_TYPES)


@app.route('/services/log/<student_id>', methods=['GET', 'POST'])
def log_service_session(student_id):
    if request.method == 'POST':
        log_session(
            student_id=student_id,
            service_id=request.form.get('service_id', ''),
            date=request.form.get('date', datetime.now().strftime('%Y-%m-%d')),
            minutes_delivered=int(request.form.get('minutes', 0)),
            notes=request.form.get('notes', ''),
        )
        flash("Session logged!", "success")
        return redirect(url_for('services_dashboard'))
    
    student = get_student(student_id)
    services_data = get_student_services(student_id)
    return render_template('services_log.html', student=student, services=services_data.get('services', []))


# ============================================================
# COMPLIANCE CALENDAR ROUTES
# ============================================================

@app.route('/compliance')
def compliance_calendar():
    students = get_all_students()
    dashboard = get_compliance_dashboard(students)
    return render_template('compliance_calendar.html',
                         dashboard=dashboard,
                         students=students)


@app.route('/compliance/add', methods=['POST'])
def compliance_add_event():
    title = request.form.get('title', '').strip()
    deadline = request.form.get('deadline', '').strip()
    student_id = request.form.get('student_id', '')
    notes = request.form.get('notes', '')
    recurring = request.form.get('recurring') == 'yes'

    if not title or not deadline:
        flash('Please provide a title and date.', 'error')
        return redirect(url_for('compliance_calendar'))

    # Get student name if a student was selected
    student_name = 'All Students'
    if student_id:
        student = get_student(student_id)
        if student:
            student_name = student.get('name', 'Unknown')

    add_custom_event({
        'title': title,
        'deadline': deadline,
        'student_id': student_id,
        'student_name': student_name,
        'recurring': recurring,
        'notes': notes,
    })
    flash(f'Deadline "{title}" added! 📋', 'success')
    return redirect(url_for('compliance_calendar'))


@app.route('/compliance/delete/<event_id>', methods=['POST'])
def compliance_delete_event(event_id):
    removed = remove_custom_event(event_id)
    if removed:
        flash('Deadline removed.', 'info')
    else:
        flash('Event not found.', 'error')
    return redirect(url_for('compliance_calendar'))




if __name__ == '__main__':
    ensure_data_dir()
    os.makedirs(PLANS_DIR, exist_ok=True)
    
    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("\n" + "="*50)
    print("  🌟 SPARK is running!")
    print("  Open your browser to: http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    app.run(debug=False, port=5000)
