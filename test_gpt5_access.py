"""
Simple test to check GPT-5-2025-08-07 accessibility
"""

import os
from model_client_clean import OpenAIClient

def test_gpt5_access():
    """Test if GPT-5-2025-08-07 is accessible"""
    
    api_key = os.getenv('OPENAI_API')
    if not api_key:
        print("No API key available")
        return False
    
    try:
        client = OpenAIClient(model='gpt-5-2025-08-07', api_key=api_key)
        completion = client.complete(
            system='You are a helpful assistant.',
            user='Say hello and confirm you are GPT-5-2025-08-07',
            max_tokens=50
        )
        print(f'SUCCESS: {completion.text}')
        print(f'Latency: {completion.latency_s:.2f}s')
        return True
    except Exception as e:
        print(f'ERROR: {e}')
        return False

if __name__ == "__main__":
    test_gpt5_access()
