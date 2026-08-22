"""
Anonymizer Module
Maps real student names to anonymous identifiers for privacy-safe prompt generation.
Stores mapping for reverse-mapping when processing responses.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
MAPPINGS_FILE = os.path.join(DATA_DIR, 'anonymizer_mappings.json')


class Anonymizer:
    """Handles name anonymization and de-anonymization."""
    
    def __init__(self):
        self.current_mapping = {}  # real_name -> anonymous_name
        self.reverse_mapping = {}  # anonymous_name -> real_name
    
    def create_mapping(self, students):
        """
        Create anonymization mapping for a list of students.
        Returns the mapping dict.
        """
        self.current_mapping = {}
        self.reverse_mapping = {}
        
        for i, student in enumerate(students, 1):
            anon_name = f"Child {i}"
            real_name = student['name']
            self.current_mapping[real_name] = anon_name
            # Also map first name alone (IEP goals often use just first name)
            first_name = real_name.split()[0] if ' ' in real_name else None
            if first_name and first_name not in self.current_mapping:
                self.current_mapping[first_name] = anon_name
            self.reverse_mapping[anon_name] = real_name
        
        # Save mapping for later de-anonymization
        self._save_mapping()
        
        return self.current_mapping
    
    def anonymize_text(self, text, students):
        """Replace all real names with anonymous identifiers in text."""
        if not self.current_mapping:
            self.create_mapping(students)
        
        result = text
        # Sort by name length (longest first) to avoid partial replacements
        sorted_names = sorted(self.current_mapping.keys(), key=len, reverse=True)
        for real_name in sorted_names:
            result = result.replace(real_name, self.current_mapping[real_name])
        
        return result
    
    def anonymize_student_data(self, student):
        """
        Create an anonymized version of student data for prompt inclusion.
        Keeps all IEP/needs info but replaces the real name everywhere —
        including inside goal text, notes, and other free-text fields.
        """
        anon_name = self.current_mapping.get(student['name'], 'Unknown Child')
        
        def _scrub(value):
            """Replace real names in a string or list of strings."""
            if isinstance(value, str):
                return self.anonymize_text(value, [student])
            elif isinstance(value, list):
                return [self.anonymize_text(item, [student]) if isinstance(item, str) else item for item in value]
            return value
        
        return {
            'name': anon_name,
            'age': student.get('age', ''),
            'grade': student.get('grade', ''),
            'iep_goals': _scrub(student.get('iep_goals', [])),
            'related_services': _scrub(student.get('related_services', '')),
            'sdi_notes': _scrub(student.get('sdi_notes', '')),
            'physical_needs': _scrub(student.get('physical_needs', [])),
            'cognitive_needs': _scrub(student.get('cognitive_needs', '')),
            'behavioral_needs': _scrub(student.get('behavioral_needs', '')),
            'sensory_needs': _scrub(student.get('sensory_needs', '')),
            'communication_mode': _scrub(student.get('communication_mode', '')),
            'communication_details': _scrub(student.get('communication_details', '')),
            'reinforcers': _scrub(student.get('reinforcers', '')),
            'life_skills_priorities': _scrub(student.get('life_skills_priorities', [])),
            'homeroom_attends': student.get('homeroom_attends', False),
            'homeroom_duration': student.get('homeroom_duration', ''),
            'homeroom_aide_accompanies': student.get('homeroom_aide_accompanies', False),
            'homeroom_schedule': student.get('homeroom_schedule', ''),
            'focus_areas': _scrub(student.get('focus_areas', [])),
            'notes': _scrub(student.get('notes', '')),
        }
    
    def deanonymize_text(self, text, mapping_id=None):
        """Replace anonymous identifiers with real names in text."""
        if mapping_id:
            self._load_mapping(mapping_id)
        
        if not self.reverse_mapping:
            self._load_latest_mapping()
        
        result = text
        # Sort by anonymous name length (longest first like "Child 10" before "Child 1")
        sorted_anon = sorted(self.reverse_mapping.keys(), key=len, reverse=True)
        for anon_name in sorted_anon:
            result = result.replace(anon_name, self.reverse_mapping[anon_name])
        
        return result
    
    def get_current_mapping(self):
        """Get the current name mapping."""
        return {
            'mapping': self.current_mapping,
            'reverse': self.reverse_mapping
        }
    
    def _save_mapping(self):
        """Save current mapping to file for later use."""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        mappings = self._load_all_mappings()
        
        mapping_entry = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'created_at': datetime.now().isoformat(),
            'mapping': self.current_mapping,
            'reverse': self.reverse_mapping
        }
        
        mappings.append(mapping_entry)
        
        # Keep only last 50 mappings
        if len(mappings) > 50:
            mappings = mappings[-50:]
        
        with open(MAPPINGS_FILE, 'w') as f:
            json.dump(mappings, f, indent=2)
    
    def _load_latest_mapping(self):
        """Load the most recent mapping."""
        mappings = self._load_all_mappings()
        if mappings:
            latest = mappings[-1]
            self.current_mapping = latest.get('mapping', {})
            self.reverse_mapping = latest.get('reverse', {})
    
    def _load_mapping(self, mapping_id):
        """Load a specific mapping by ID."""
        mappings = self._load_all_mappings()
        for m in mappings:
            if m['id'] == mapping_id:
                self.current_mapping = m.get('mapping', {})
                self.reverse_mapping = m.get('reverse', {})
                return
    
    def _load_all_mappings(self):
        """Load all saved mappings."""
        if not os.path.exists(MAPPINGS_FILE):
            return []
        try:
            with open(MAPPINGS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
