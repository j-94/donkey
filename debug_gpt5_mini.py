"""
Debug script to see what GPT-5-mini-2025-08-07 actually returns
"""

import os
from model_client_clean import OpenAIClient

def debug_gpt5_mini_response():
    """Test what GPT-5-mini-2025-08-07 actually returns"""
    
    api_key = os.getenv("OPENAI_API")
    if not api_key:
        print("No API key available")
        return
    
    client = OpenAIClient(model="gpt-5-mini-2025-08-07", temperature=0.0, api_key=api_key)
    
    simple_prompt = "Write a Python function that adds two numbers."
    
    print("=== TESTING GPT-5-mini-2025-08-07 RAW RESPONSE ===")
    print(f"Prompt: {simple_prompt}")
    print("\n" + "="*50)
    
    completion = client.complete(
        system="You are a Python code generator. Output only code, no markdown.",
        user=simple_prompt,
        temperature=0.0
    )
    
    print(f"Latency: {completion.latency_s:.2f}s")
    print(f"Response length: {len(completion.text)} characters")
    print(f"Response type: {type(completion.text)}")
    print("\nRaw response:")
    print(repr(completion.text))
    print("\nFormatted response:")
    print(completion.text)
    print("\n" + "="*50)
    
    from csce_generator import create_csce_prompt, CSCE_SYSTEM_PROMPT
    
    csce_prompt = create_csce_prompt("add_numbers", "a, b", simple_prompt, budget_sec=30)
    
    print("\n=== TESTING CSCE v2.3 PROMPT ===")
    print("CSCE prompt preview:")
    print(csce_prompt[:200] + "..." if len(csce_prompt) > 200 else csce_prompt)
    print("\n" + "="*50)
    
    csce_completion = client.complete(
        system=CSCE_SYSTEM_PROMPT,
        user=csce_prompt,
        temperature=0.0
    )
    
    print(f"CSCE Latency: {csce_completion.latency_s:.2f}s")
    print(f"CSCE Response length: {len(csce_completion.text)} characters")
    print("\nCSCE Raw response:")
    print(repr(csce_completion.text))
    print("\nCSCE Formatted response:")
    print(csce_completion.text)
    
    if "STATE_SIG:" in csce_completion.text:
        print("✓ STATE_SIG found in CSCE response")
    else:
        print("⚠ STATE_SIG missing from CSCE response")

if __name__ == "__main__":
    debug_gpt5_mini_response()
