import os
import requests
import logging
from typing import Dict

logger = logging.getLogger('aurelium.ai')


def send_to_provider(prompt: str, model: str | None = None) -> Dict:
    """Send prompt to configured AI provider and return parsed response.

    Supported providers via `AI_PROVIDER` env var: `openai`, `groq`.
    The `AI_API_KEY` env var must be set to enable proxying.
    """
    provider = os.getenv('AI_PROVIDER', 'openai').lower()
    api_key = os.getenv('AI_API_KEY')
    if not api_key:
        raise RuntimeError('AI_API_KEY not configured')

    if provider == 'openai':
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        payload = {
            'model': model or os.getenv('AI_MODEL', 'gpt-4o-mini'),
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.2,
        }
        logger.info('Proxying prompt to OpenAI model=%s', payload['model'])
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        # Normalize response: extract text
        text = None
        try:
            text = data['choices'][0]['message']['content']
        except Exception:
            text = data.get('error') or str(data)
        return {'provider': 'openai', 'raw': data, 'text': text}

    if provider == 'groq':
        url = os.getenv('GROQ_API_URL', 'https://api.groq.ai/v1/chat/completions')
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        payload = {
            'model': model or os.getenv('AI_MODEL', 'llama-3.1-405b-reasoning'),
            'messages': [{'role': 'user', 'content': prompt}],
        }
        logger.info('Proxying prompt to Groq model=%s', payload['model'])
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        text = None
        try:
            text = data['choices'][0]['message']['content']
        except Exception:
            text = data.get('error') or str(data)
        return {'provider': 'groq', 'raw': data, 'text': text}

    raise RuntimeError(f'Unsupported AI_PROVIDER: {provider}')
