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
# ROUTES
# ============================================================

@app.route('/')
def dashboard():
    config = get_config()
    if not config.get('setup_complete'):
        return redirect(url_for('setup_wizard'))
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
            'iep_goals': [g.strip() for g in request.form.get('iep_goals', '').split('\n') if g.strip()],
            'iep_annual_review_date': request.form.get('iep_annual_review_date', ''),
            'related_services': request.form.get('related_services', ''),
            'sdi_notes': request.form.get('sdi_notes', ''),
            'physical_needs': [n.strip() for n in request.form.get('physical_needs', '').split('\n') if n.strip()],
            'cognitive_needs': request.form.get('cognitive_needs', ''),
            'behavioral_needs': request.form.get('behavioral_needs', ''),
            'sensory_needs': request.form.get('sensory_needs', ''),
            'communication_mode': request.form.get('communication_mode', ''),
            'communication_details': request.form.get('communication_details', ''),
            'homeroom_attends': request.form.get('homeroom_attends') == 'yes',
            'homeroom_duration': request.form.get('homeroom_duration', ''),
            'homeroom_aide_accompanies': request.form.get('homeroom_aide_accompanies') == 'yes',
            'homeroom_schedule': request.form.get('homeroom_schedule', ''),
            'focus_areas': [a.strip() for a in request.form.get('focus_areas', '').split('\n') if a.strip()],
            'reinforcers': request.form.get('reinforcers', ''),
            'life_skills_priorities': [l.strip() for l in request.form.get('life_skills_priorities', '').split('\n') if l.strip()],
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
            'iep_goals': [g.strip() for g in request.form.get('iep_goals', '').split('\n') if g.strip()],
            'iep_annual_review_date': request.form.get('iep_annual_review_date', ''),
            'related_services': request.form.get('related_services', ''),
            'sdi_notes': request.form.get('sdi_notes', ''),
            'physical_needs': [n.strip() for n in request.form.get('physical_needs', '').split('\n') if n.strip()],
            'cognitive_needs': request.form.get('cognitive_needs', ''),
            'behavioral_needs': request.form.get('behavioral_needs', ''),
            'sensory_needs': request.form.get('sensory_needs', ''),
            'communication_mode': request.form.get('communication_mode', ''),
            'communication_details': request.form.get('communication_details', ''),
            'homeroom_attends': request.form.get('homeroom_attends') == 'yes',
            'homeroom_duration': request.form.get('homeroom_duration', ''),
            'homeroom_aide_accompanies': request.form.get('homeroom_aide_accompanies') == 'yes',
            'homeroom_schedule': request.form.get('homeroom_schedule', ''),
            'focus_areas': [a.strip() for a in request.form.get('focus_areas', '').split('\n') if a.strip()],
            'reinforcers': request.form.get('reinforcers', ''),
            'life_skills_priorities': [l.strip() for l in request.form.get('life_skills_priorities', '').split('\n') if l.strip()],
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
        
        builder = PromptBuilder()
        prompt = builder.build_prompt(
            students=students,
            config=config,
            plan_type=plan_type,
            month_override=selected_month if selected_month else None,
            custom_theme=custom_theme,
            additional_notes=additional_notes
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
        config['num_dedicated_aides'] = int(request.form.get('num_dedicated_aides', 2))
        config['aide_names'] = request.form.getlist('aide_names')
        # Ensure we have enough aide names
        while len(config['aide_names']) < config['num_dedicated_aides']:
            config['aide_names'].append(f"Aide {len(config['aide_names']) + 1}")
        config['aide_names'] = config['aide_names'][:config['num_dedicated_aides']]
        
        config['has_floater'] = request.form.get('has_floater') == 'yes'
        config['floater_name'] = request.form.get('floater_name', 'Floater')
        config['min_aides_in_own_room'] = int(request.form.get('min_aides_in_own_room', 1))
        config['min_aides_in_partner_room'] = 1  # Hard rule: always 1 aide in partner room
        
        config['partner_teacher'] = {
            'enabled': request.form.get('partner_enabled') == 'yes',
            'name': request.form.get('partner_name', ''),
            'num_aides': int(request.form.get('partner_num_aides', 2)),
            'aide_names': [f"Partner Aide {i+1}" for i in range(int(request.form.get('partner_num_aides', 2)))],
            'num_students': int(request.form.get('partner_num_students', 0)),
            'shared_floater': request.form.get('shared_floater') == 'yes',
            'notes': request.form.get('partner_notes', '')
        }
        
        config['configured'] = True
        save_schedule_config(config)
        
        # Auto-generate schedule
        students = get_all_students()
        if students:
            generated = generate_schedule(students, config)
            schedule_file = os.path.join(DATA_DIR, 'current_schedule.json')
            with open(schedule_file, 'w') as f:
                json.dump(generated, f, indent=2)
            flash('Staffing saved and schedule generated! 📅', 'success')
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
    
    generated = generate_schedule(students, config)
    schedule_file = os.path.join(DATA_DIR, 'current_schedule.json')
    with open(schedule_file, 'w') as f:
        json.dump(generated, f, indent=2)
    
    flash('Schedule regenerated! ✅', 'success')
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
    return render_template('settings.html', config=config)


# --- Update Routes ---

@app.route('/check-updates')
def check_updates():
    result = check_for_updates()
    return jsonify(result)


@app.route('/apply-update', methods=['POST'])
def do_update():
    result = apply_update()
    return jsonify(result)


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
        
        if student_id and goal_text and value:
            from datetime import date
            add_data_point(student_id, goal_text, date.today().isoformat(), value, method, notes)
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

def open_browser():
    """Open browser after a short delay to let the server start."""
    import time
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')


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
