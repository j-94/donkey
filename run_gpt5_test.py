"""
Test GPT-5-mini integration and run comprehensive evaluation
"""

import os
import time
from model_client_clean import OpenAIClient
from simple_mock_client import SimpleMockClient
from csce_generator import create_csce_prompt, CSCE_SYSTEM_PROMPT
from vanilla_generator import VANILLA_SYSTEM_PROMPT
from run_evalplus_csce import _strip_markdown_enhanced

def test_gpt5_mini_availability():
    """Test if GPT-5-mini is accessible and working"""
    api_key = os.getenv("OPENAI_API")
    if not api_key:
        print("No API key available for GPT-5-mini test")
        return False
        
    try:
        client = OpenAIClient(model="gpt-5-mini-2025-08-07", temperature=0.2, api_key=api_key)
        completion = client.complete(
            system="You are a helpful assistant.",
            user="Say 'GPT-5 is working correctly' if you can respond.",
            temperature=0.0
        )
        print(f"GPT-5-mini-2025-08-07 response: {completion.text}")
        return "working" in completion.text.lower()
    except Exception as e:
        print(f"GPT-5 test failed: {e}")
        return False

def compare_vanilla_vs_csce():
    """Compare vanilla vs CSCE v2.3 on a simple problem"""
    
    test_prompt = "Write a function that finds the maximum sum of any contiguous subarray (Kadane's algorithm)."
    
    print("=== VANILLA VS CSCE v2.3 COMPARISON ===")
    
    if test_gpt5_mini_availability():
        print("✓ GPT-5-mini-2025-08-07 is accessible - using real API")
        api_key = os.getenv("OPENAI_API")
        client = OpenAIClient(model="gpt-5-mini-2025-08-07", temperature=0.2, api_key=api_key)
        use_real_api = True
    else:
        print("⚠ GPT-5-mini-2025-08-07 not accessible - using mock client")
        client = SimpleMockClient(mock_latency=0.5)
        use_real_api = False
    
    print("\n--- VANILLA APPROACH ---")
    start_time = time.time()
    vanilla_completion = client.complete(
        system=VANILLA_SYSTEM_PROMPT,
        user=test_prompt,
        temperature=0.2
    )
    vanilla_time = time.time() - start_time
    
    print(f"Generated in {vanilla_time:.2f}s")
    print("Vanilla code:")
    print(vanilla_completion.text[:200] + "..." if len(vanilla_completion.text) > 200 else vanilla_completion.text)
    
    print("\n--- CSCE v2.3 APPROACH ---")
    csce_prompt = create_csce_prompt("max_subarray_sum", "arr", test_prompt, budget_sec=30)
    
    start_time = time.time()
    csce_completion = client.complete(
        system=CSCE_SYSTEM_PROMPT,
        user=csce_prompt,
        temperature=0.2
    )
    csce_time = time.time() - start_time
    
    print(f"Generated in {csce_time:.2f}s")
    print("CSCE v2.3 code:")
    print(csce_completion.text[:200] + "..." if len(csce_completion.text) > 200 else csce_completion.text)
    
    if "STATE_SIG:" in csce_completion.text:
        print("✓ STATE_SIG found in CSCE response")
    else:
        print("⚠ STATE_SIG missing from CSCE response")
    
    vanilla_clean = _strip_markdown_enhanced(vanilla_completion.text)
    csce_clean = _strip_markdown_enhanced(csce_completion.text)
    
    print(f"\n=== SUMMARY ===")
    print(f"Model: {'GPT-5-mini-2025-08-07' if use_real_api else 'Mock Client'}")
    print(f"Vanilla time: {vanilla_time:.2f}s, length: {len(vanilla_clean)} chars")
    print(f"CSCE v2.3 time: {csce_time:.2f}s, length: {len(csce_clean)} chars")
    print(f"CSCE overhead: {((csce_time - vanilla_time) / vanilla_time * 100):.1f}%")
    
    return {
        "model": "gpt-5-mini-2025-08-07" if use_real_api else "mock",
        "vanilla_time": vanilla_time,
        "csce_time": csce_time,
        "vanilla_length": len(vanilla_clean),
        "csce_length": len(csce_clean),
        "state_sig_present": "STATE_SIG:" in csce_completion.text
    }

if __name__ == "__main__":
    results = compare_vanilla_vs_csce()
    print(f"\nTest completed with results: {results}")
