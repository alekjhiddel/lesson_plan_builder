"""
Scraper Module
Fetches web content, extracts useful text, and saves to local knowledge base.
"""

import os
import json
import uuid
import re
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
KB_DIR = os.path.join(DATA_DIR, 'knowledge_base')


def scrape_url(url):
    """
    Scrape a URL and save useful content to the knowledge base.
    Returns dict with success status and extracted info.
    """
    if not HAS_DEPS:
        return {'success': False, 'error': 'Required packages not installed. Run: pip install requests beautifulsoup4'}
    
    os.makedirs(KB_DIR, exist_ok=True)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Get title
        title = soup.title.string if soup.title else url
        title = title.strip() if title else url
        
        # Get main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            # Extract text with some structure
            text_parts = []
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td']):
                text = element.get_text(strip=True)
                if text and len(text) > 10:
                    if element.name.startswith('h'):
                        text_parts.append(f"\n## {text}\n")
                    elif element.name == 'li':
                        text_parts.append(f"• {text}")
                    else:
                        text_parts.append(text)
            
            content = '\n'.join(text_parts)
        else:
            content = soup.get_text(separator='\n', strip=True)
        
        # Clean up
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content[:10000]  # Limit size
        
        # Create summary (first 500 chars of meaningful content)
        summary_text = ' '.join(content.split()[:100])
        
        # Save to knowledge base
        resource = {
            'id': str(uuid.uuid4()),
            'url': url,
            'title': title[:200],
            'content': content,
            'summary': summary_text,
            'scraped_at': datetime.now().isoformat()
        }
        
        filename = f"{resource['id']}.json"
        filepath = os.path.join(KB_DIR, filename)
        with open(filepath, 'w') as f:
            json.dump(resource, f, indent=2)
        
        return {
            'success': True,
            'title': title,
            'summary': summary_text,
            'content_length': len(content)
        }
    
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'The website took too long to respond. Try again later.'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Could not reach the website: {str(e)[:100]}'}
    except Exception as e:
        return {'success': False, 'error': f'Something went wrong: {str(e)[:100]}'}


def get_knowledge_base():
    """Get all resources in the knowledge base."""
    if not os.path.exists(KB_DIR):
        return []
    
    resources = []
    for filename in sorted(os.listdir(KB_DIR), reverse=True):
        if filename.endswith('.json'):
            filepath = os.path.join(KB_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    resource = json.load(f)
                    resources.append(resource)
            except:
                continue
    
    return resources


def delete_resource(resource_id):
    """Delete a knowledge base resource by ID."""
    if not os.path.exists(KB_DIR):
        return False
    
    for filename in os.listdir(KB_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(KB_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    resource = json.load(f)
                if resource.get('id') == resource_id:
                    os.remove(filepath)
                    return True
            except:
                continue
    return False
