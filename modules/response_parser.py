"""
Response Parser Module
Processes ChatGPT responses: de-anonymizes names, formats output, saves plans.
"""

from .anonymizer import Anonymizer


class ResponseParser:
    """Processes and de-anonymizes ChatGPT lesson plan responses."""
    
    def __init__(self):
        self.anonymizer = Anonymizer()
    
    def process_response(self, raw_response, students):
        """
        Process a raw ChatGPT response:
        1. De-anonymize student names
        2. Format for display
        3. Return processed text
        """
        # Load the most recent anonymization mapping
        self.anonymizer._load_latest_mapping()
        
        # De-anonymize the text
        processed = self.anonymizer.deanonymize_text(raw_response)
        
        return processed
    
    def format_for_print(self, processed_text):
        """Format processed text for clean printing."""
        # Add some basic formatting improvements
        lines = processed_text.split('\n')
        formatted = []
        
        for line in lines:
            # Make headers stand out
            if line.startswith('# '):
                formatted.append(f'\n{"="*60}')
                formatted.append(line[2:].upper())
                formatted.append(f'{"="*60}')
            elif line.startswith('## '):
                formatted.append(f'\n{"-"*40}')
                formatted.append(line[3:])
                formatted.append(f'{"-"*40}')
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)
