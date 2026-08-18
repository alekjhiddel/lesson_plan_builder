"""
Updater Module
Checks GitHub for new releases, downloads updates, and applies them
while preserving user data. Also handles schema migrations.
"""

import os
import json
import shutil
import zipfile
import tempfile
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(APP_DIR, 'data')
VERSION_FILE = os.path.join(APP_DIR, 'version.json')
BACKUP_DIR = os.path.join(APP_DIR, 'backups')

# GitHub repo info
GITHUB_REPO = 'alekjhiddel/lesson_plan_builder'
GITHUB_API = f'https://api.github.com/repos/{GITHUB_REPO}'
GITHUB_ZIP = f'https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip'

# Current app version
CURRENT_VERSION = '1.1.0'
SCHEMA_VERSION = 1


def get_current_version():
    """Get the current installed version."""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            return json.load(f)
    return {
        'version': CURRENT_VERSION,
        'schema_version': SCHEMA_VERSION,
        'updated_at': None,
        'installed_at': datetime.now().isoformat()
    }


def save_version_info(version_info):
    """Save version info."""
    with open(VERSION_FILE, 'w') as f:
        json.dump(version_info, f, indent=2)


def check_for_updates():
    """
    Check GitHub for the latest version.
    Returns dict with: available, latest_version, current_version, changes
    Always returns a user-visible 'message' field.
    """
    if not HAS_REQUESTS:
        return {'available': False, 'error': 'requests package not installed'}
    
    try:
        # Get latest commit info
        response = requests.get(
            f'{GITHUB_API}/commits/main',
            headers={'Accept': 'application/vnd.github.v3+json'},
            timeout=10
        )
        
        if response.status_code != 200:
            return {'available': False, 'error': f'GitHub returned status {response.status_code}'}
        
        latest = response.json()
        latest_sha = latest['sha'][:7]
        latest_date = latest['commit']['committer']['date']
        latest_message = latest['commit']['message']
        
        # Check if we have version.json with last update SHA
        current = get_current_version()
        current_sha = current.get('last_commit_sha', '')
        current_version = current.get('version', CURRENT_VERSION)
        
        # Also fetch the remote version.json to compare version strings
        # This handles fresh installs where last_commit_sha isn't set
        remote_version = None
        try:
            ver_resp = requests.get(
                f'https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.json',
                timeout=10
            )
            if ver_resp.status_code == 200:
                remote_version = ver_resp.json().get('version', '')
        except:
            pass
        
        # Up to date if EITHER:
        # 1. SHA matches (we installed this exact commit), OR
        # 2. Version strings match (fresh install from same release)
        is_up_to_date = False
        if current_sha and current_sha == latest_sha:
            is_up_to_date = True
        elif remote_version and remote_version == current_version and not current_sha:
            # Fresh install, same version — stamp the SHA so future checks are fast
            current['last_commit_sha'] = latest_sha
            save_version_info(current)
            is_up_to_date = True
        
        if is_up_to_date:
            return {
                'available': False,
                'current_version': current_version,
                'latest_version': remote_version or current_version,
                'message': f'You\'re on the latest version (v{current_version}). No update needed! ✅'
            }
        
        # Get recent commits to show what changed
        response2 = requests.get(
            f'{GITHUB_API}/commits',
            params={'per_page': 10},
            headers={'Accept': 'application/vnd.github.v3+json'},
            timeout=10
        )
        
        changes = []
        if response2.status_code == 200:
            commits = response2.json()
            for commit in commits[:5]:
                sha = commit['sha'][:7]
                msg = commit['commit']['message'].split('\n')[0]
                date = commit['commit']['committer']['date'][:10]
                changes.append(f'{date}: {msg}')
                if sha == current_sha:
                    break
        
        return {
            'available': True,
            'current_version': current_version,
            'latest_version': remote_version or 'newer',
            'latest_sha': latest_sha,
            'latest_date': latest_date[:10],
            'latest_message': latest_message,
            'changes': changes,
            'message': f'Update available! You have v{current_version}, latest is v{remote_version or "?"} ({latest_date[:10]})'
        }
    
    except requests.exceptions.Timeout:
        return {'available': False, 'error': 'Could not reach GitHub (timeout). Check your internet connection.'}
    except requests.exceptions.ConnectionError:
        return {'available': False, 'error': 'No internet connection. Connect to WiFi and try again.'}
    except Exception as e:
        return {'available': False, 'error': f'Something went wrong: {str(e)[:100]}'}


def apply_update():
    """
    Download latest from GitHub and apply update.
    Preserves: data/, venv/, backups/
    Returns dict with success status.
    """
    if not HAS_REQUESTS:
        return {'success': False, 'error': 'requests package not installed'}
    
    try:
        # Step 1: Backup current data
        backup_result = create_backup()
        if not backup_result['success']:
            return {'success': False, 'error': f'Backup failed: {backup_result["error"]}'}
        
        # Step 2: Download latest zip from GitHub
        response = requests.get(GITHUB_ZIP, timeout=30, stream=True)
        if response.status_code != 200:
            return {'success': False, 'error': f'Download failed (status {response.status_code})'}
        
        # Step 3: Save to temp file
        temp_zip = os.path.join(tempfile.gettempdir(), 'spark_update.zip')
        with open(temp_zip, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Step 4: Extract to temp directory
        temp_extract = os.path.join(tempfile.gettempdir(), 'spark_update_extract')
        if os.path.exists(temp_extract):
            shutil.rmtree(temp_extract)
        
        with zipfile.ZipFile(temp_zip, 'r') as zf:
            zf.extractall(temp_extract)
        
        # Find the extracted folder (GitHub adds repo-branch prefix)
        extracted_dirs = os.listdir(temp_extract)
        if not extracted_dirs:
            return {'success': False, 'error': 'Downloaded zip was empty'}
        
        source_dir = os.path.join(temp_extract, extracted_dirs[0])
        
        # Step 5: Replace code files (preserve data/, venv/, backups/)
        preserve = {'data', 'venv', 'backups', '.git', '__pycache__'}
        
        # Remove old code files
        for item in os.listdir(APP_DIR):
            item_path = os.path.join(APP_DIR, item)
            if item in preserve:
                continue
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        
        # Copy new files in
        for item in os.listdir(source_dir):
            src = os.path.join(source_dir, item)
            dst = os.path.join(APP_DIR, item)
            if item in preserve:
                continue
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        # Step 6: Update version info
        # Get the SHA we just downloaded
        try:
            resp = requests.get(
                f'{GITHUB_API}/commits/main',
                headers={'Accept': 'application/vnd.github.v3+json'},
                timeout=10
            )
            if resp.status_code == 200:
                new_sha = resp.json()['sha'][:7]
            else:
                new_sha = 'unknown'
        except:
            new_sha = 'unknown'
        
        version_info = get_current_version()
        version_info['last_commit_sha'] = new_sha
        version_info['updated_at'] = datetime.now().isoformat()
        save_version_info(version_info)
        
        # Step 7: Run schema migrations
        migration_result = run_migrations()
        
        # Cleanup
        os.remove(temp_zip)
        shutil.rmtree(temp_extract)
        
        # Restore executable permissions on start scripts (GitHub zips strip them)
        start_command = os.path.join(APP_DIR, 'start.command')
        if os.path.exists(start_command):
            import stat
            os.chmod(start_command, os.stat(start_command).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        return {
            'success': True,
            'message': 'Update applied successfully! ✅ Restart the app to see changes.',
            'backup_path': backup_result.get('path'),
            'migrations_run': migration_result.get('migrations_applied', 0)
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Update failed: {str(e)[:200]}'}


def create_backup():
    """Create a backup of the data folder."""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(BACKUP_DIR, f'data_backup_{timestamp}')
        
        if os.path.exists(DATA_DIR):
            shutil.copytree(DATA_DIR, backup_path)
        
        # Keep only last 5 backups
        backups = sorted([
            d for d in os.listdir(BACKUP_DIR) 
            if os.path.isdir(os.path.join(BACKUP_DIR, d))
        ])
        while len(backups) > 5:
            oldest = os.path.join(BACKUP_DIR, backups.pop(0))
            shutil.rmtree(oldest)
        
        return {'success': True, 'path': backup_path}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def run_migrations():
    """
    Run schema migrations to upgrade data format.
    Each migration is a function that transforms data from version N to N+1.
    """
    config_path = os.path.join(DATA_DIR, 'config.json')
    if not os.path.exists(config_path):
        return {'migrations_applied': 0}
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    current_schema = config.get('schema_version', 0)
    migrations_applied = 0
    
    # Migration 1: Add schema_version, add new student fields
    if current_schema < 1:
        _migrate_to_v1()
        current_schema = 1
        migrations_applied += 1
    
    # Migration 2: (future) Add SPARK fields, rename tool
    if current_schema < 2:
        _migrate_to_v2()
        current_schema = 2
        migrations_applied += 1
    
    # Save updated schema version
    config['schema_version'] = current_schema
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return {'migrations_applied': migrations_applied, 'current_schema': current_schema}


def _migrate_to_v1():
    """Migration 0 → 1: Ensure all student fields exist."""
    students_path = os.path.join(DATA_DIR, 'students.json')
    if not os.path.exists(students_path):
        return
    
    with open(students_path, 'r') as f:
        students = json.load(f)
    
    new_fields = {
        'behavioral_needs': '',
        'sensory_needs': '',
        'reinforcers': '',
        'life_skills_priorities': [],
        'related_services': '',
        'sdi_notes': '',
        'iep_annual_review_date': '',
        'progress_notes': [],
        'prompting_level': ''
    }
    
    for student in students:
        for field, default in new_fields.items():
            if field not in student:
                student[field] = default
    
    with open(students_path, 'w') as f:
        json.dump(students, f, indent=2)


def _migrate_to_v2():
    """Migration 1 → 2: Add SPARK-era fields."""
    config_path = os.path.join(DATA_DIR, 'config.json')
    if not os.path.exists(config_path):
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Add new config fields if missing
    new_config_fields = {
        'app_name': 'SPARK',
        'program_type': 'msd',  # msd, lbd, preschool, resource, inclusion, transition
        'grade_level': 'elementary',
        'state': 'KY',
        'school_year': '',
        'nti_parent_has_internet': True,
        'nti_parent_has_printer': False,
    }
    
    for field, default in new_config_fields.items():
        if field not in config:
            config[field] = default
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Add new student fields
    students_path = os.path.join(DATA_DIR, 'students.json')
    if os.path.exists(students_path):
        with open(students_path, 'r') as f:
            students = json.load(f)
        
        spark_fields = {
            'program_type': 'msd',
            'grade': '',
            'transition_goals': [],
            'parent_contact_pref': '',
            'nti_accommodations': '',
            'medical_alerts': [],
            'behavior_plan_summary': '',
            'related_service_minutes': {},
        }
        
        for student in students:
            for field, default in spark_fields.items():
                if field not in student:
                    student[field] = default
        
        with open(students_path, 'w') as f:
            json.dump(students, f, indent=2)



def export_backup_zip(destination_path=None):
    """
    Export all user data to a single zip file for safekeeping.
    Teacher can save this to USB, external drive, etc.
    Returns the path to the created zip file.
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if destination_path:
            zip_path = destination_path
        else:
            # Default: save next to the app folder
            zip_path = os.path.join(APP_DIR, f'SPARK_backup_{timestamp}.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Back up the data/ folder
            if os.path.exists(DATA_DIR):
                for root, dirs, files in os.walk(DATA_DIR):
                    for fname in files:
                        filepath = os.path.join(root, fname)
                        arcname = os.path.join('data', os.path.relpath(filepath, DATA_DIR))
                        zf.write(filepath, arcname)
            
            # Back up version.json
            if os.path.exists(VERSION_FILE):
                zf.write(VERSION_FILE, 'version.json')
        
        size = os.path.getsize(zip_path)
        
        return {
            'success': True,
            'path': zip_path,
            'filename': os.path.basename(zip_path),
            'size': size,
            'size_readable': f'{size / 1024:.1f} KB' if size < 1048576 else f'{size / 1048576:.1f} MB',
            'message': f'Backup saved! ({size / 1024:.1f} KB)'
        }
    except Exception as e:
        return {'success': False, 'error': f'Backup failed: {str(e)[:200]}'}


def restore_from_zip(zip_path):
    """
    Restore data from a backup zip file.
    Replaces current data/ folder with the backed-up version.
    Creates a safety backup of current data first.
    """
    try:
        if not os.path.exists(zip_path):
            return {'success': False, 'error': 'Backup file not found'}
        
        # Safety: backup current data first
        safety_backup = create_backup()
        
        # Verify the zip contains a data/ folder
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            has_data = any(n.startswith('data/') for n in names)
            if not has_data:
                return {'success': False, 'error': 'This zip does not contain SPARK data. Make sure you selected a SPARK backup file.'}
            
            # Remove current data/ and extract backup
            if os.path.exists(DATA_DIR):
                shutil.rmtree(DATA_DIR)
            
            # Extract only data/ folder
            for name in names:
                if name.startswith('data/'):
                    zf.extract(name, APP_DIR)
        
        # Run migrations in case the backup is from an older version
        migration_result = run_migrations()
        
        return {
            'success': True,
            'message': 'Data restored successfully! Refresh the page to see your data.',
            'safety_backup': safety_backup.get('path', ''),
            'migrations_run': migration_result.get('migrations_applied', 0)
        }
    except zipfile.BadZipFile:
        return {'success': False, 'error': 'The file is not a valid zip archive.'}
    except Exception as e:
        return {'success': False, 'error': f'Restore failed: {str(e)[:200]}'}


def list_backups():
    """List available local backups."""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for item in sorted(os.listdir(BACKUP_DIR), reverse=True):
        item_path = os.path.join(BACKUP_DIR, item)
        if os.path.isdir(item_path):
            # Get size
            size = sum(
                os.path.getsize(os.path.join(r, f))
                for r, d, files in os.walk(item_path)
                for f in files
            )
            backups.append({
                'name': item,
                'path': item_path,
                'date': item.replace('data_backup_', '').replace('_', ' '),
                'size': f'{size / 1024:.1f} KB'
            })
    
    return backups
