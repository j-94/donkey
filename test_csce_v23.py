"""
Test script for CSCE v2.3 Dialogic Metaprogramming system
"""

import os
from model_client_clean import OpenAIClient
from simple_mock_client import SimpleMockClient
from csce_generator import create_csce_prompt, CSCE_SYSTEM_PROMPT

def test_gpt5_availability():
    """Test if GPT-5 is accessible"""
    api_key = os.getenv("OPENAI_API")
    if not api_key:
        print("No API key available for GPT-5 test")
        return False
        
    try:
        client = OpenAIClient(model="gpt-5-2025-08-07", temperature=0.2, api_key=api_key)
        completion = client.complete(
            system="You are a helpful assistant.",
            user="Say 'GPT-5 is working' if you can respond.",
            temperature=0.0
        )
        return "working" in completion.text.lower()
    except Exception as e:
        print(f"GPT-5 test failed: {e}")
        return False

def test_csce_v23():
    """Test the new CSCE v2.3 system with a simple problem"""
    
    test_prompt = """
Write a function that takes a list of numbers and returns the sum of all even numbers.

Example:
sum_evens([1, 2, 3, 4, 5, 6]) should return 12 (2 + 4 + 6)
"""
    
    entry_point = "sum_evens"
    params = "numbers"
    
    csce_prompt = create_csce_prompt(entry_point, params, test_prompt)
    
    print("=== CSCE v2.3 Prompt ===")
    print(csce_prompt)
    print("\n" + "="*50 + "\n")
    
    print("=== Testing GPT-5-2025-08-07 Availability ===")
    if test_gpt5_availability():
        print("✓ GPT-5-2025-08-07 is accessible")
        use_real_api = True
    else:
        print("⚠ GPT-5-2025-08-07 not accessible, using mock client")
        use_real_api = False
    
    if use_real_api:
        api_key = os.getenv("OPENAI_API")
        client = OpenAIClient(model="gpt-5-2025-08-07", temperature=0.2, api_key=api_key)
        print("=== Calling GPT-5-2025-08-07 with CSCE v2.3 ===")
    else:
        client = SimpleMockClient(mock_latency=0.5)
        print("=== Using Mock Client with CSCE v2.3 ===")
    
    completion = client.complete(
        system=CSCE_SYSTEM_PROMPT,
        user=csce_prompt,
        temperature=0.2
    )
    
    print(f"Latency: {completion.latency_s:.2f}s")
    print("Generated Code:")
    print(completion.text)
    
    try:
        from run_evalplus_csce import _strip_markdown_enhanced
        clean_code = _strip_markdown_enhanced(completion.text)
        print("Cleaned Code:")
        print(clean_code)
        print("\n" + "="*50 + "\n")
        
        namespace = {}
        exec(clean_code, namespace)
        sum_evens = namespace['sum_evens']
        result = sum_evens([1, 2, 3, 4, 5, 6])
        print(f"Test result: sum_evens([1, 2, 3, 4, 5, 6]) = {result}")
        print("Expected: 12")
        print(f"Test {'PASSED' if result == 12 else 'FAILED'}")
    except Exception as e:
        print(f"Error executing code: {e}")

if __name__ == "__main__":
    test_csce_v23()
