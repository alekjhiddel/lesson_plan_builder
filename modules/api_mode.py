"""
API Mode Module
Optional OpenAI API integration for direct prompt submission.
Off by default — works via copy/paste when disabled.
"""


def is_api_configured(config):
    """Check if API mode is properly configured."""
    return bool(config.get('api_key') and config.get('api_enabled'))


def generate_with_api(prompt, config):
    """
    Send prompt to OpenAI API and return response.
    Returns None if API is not configured or call fails.
    """
    if not is_api_configured(config):
        return None
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=config['api_key'])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert special education lesson plan designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except ImportError:
        print("OpenAI package not installed. Run: pip install openai")
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None
