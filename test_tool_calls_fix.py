"""
Test the tool_calls debugging fix for GPT-5 models
"""

import os
from model_client_clean import OpenAIClient

def test_gpt5_with_fix():
    """Test GPT-5 models with tool_calls debugging fix"""
    
    api_key = os.getenv('OPENAI_API')
    if not api_key:
        print("No API key available")
        return
    
    models_to_test = ["gpt-5-mini-2025-08-07", "gpt-5-2025-08-07"]
    
    for model in models_to_test:
        print(f"\n=== TESTING {model} ===")
        print("-" * 50)
        
        try:
            client = OpenAIClient(model=model, api_key=api_key)
            
            print("Test 1: Simple ping")
            completion = client.complete(
                system="You are a helpful assistant.",
                user="ping (reply with 'pong' only)",
                max_tokens=50
            )
            print(f"Response: '{completion.text}'")
            print(f"Length: {len(completion.text)} chars")
            print(f"Latency: {completion.latency_s:.2f}s")
            
            print("\nTest 2: Code generation")
            completion = client.complete(
                system="You are a Python code generator.",
                user="Write a function to add two numbers: def add(a, b):",
                max_tokens=200
            )
            print(f"Response: '{completion.text[:200]}...'")
            print(f"Length: {len(completion.text)} chars")
            print(f"Latency: {completion.latency_s:.2f}s")
            
        except Exception as e:
            print(f"Error with {model}: {e}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_gpt5_with_fix()
