"""
Simplified CSCE test for GPT-5-mini-2025-08-07 compatibility
"""

import os
import time
from model_client_clean import OpenAIClient
from run_evalplus_csce import _strip_markdown_enhanced

SIMPLIFIED_CSCE_SYSTEM = """You are a structured code generator that thinks step by step.

For each problem:
1. PLAN: Break down the problem into steps
2. THINK: Consider the approach and edge cases  
3. IMPLEMENT: Write clean, working Python code
4. Add a comment at the end: # STEPS: <number of logical steps taken>

Output only Python code with planning comments, no markdown fences."""

VANILLA_SYSTEM = """You are a Python code generator. Output only clean Python code, no markdown fences."""

def test_simplified_csce():
    """Test simplified CSCE vs vanilla on algorithmic problems"""
    
    api_key = os.getenv("OPENAI_API")
    if not api_key:
        print("No API key available")
        return
    
    client = OpenAIClient(model="gpt-5-mini-2025-08-07", temperature=0.0, api_key=api_key)
    
    test_problems = [
        {
            "name": "Longest Increasing Subsequence",
            "prompt": "Write a function longest_increasing_subsequence(nums) that returns the length of the longest increasing subsequence in the array. Use dynamic programming."
        },
        {
            "name": "Binary Search",
            "prompt": "Write a function binary_search(arr, target) that returns the index of target in sorted array arr, or -1 if not found."
        },
        {
            "name": "Valid Parentheses",
            "prompt": "Write a function is_valid_parentheses(s) that returns True if the string s has valid parentheses (properly opened and closed)."
        }
    ]
    
    results = {"vanilla": [], "simplified_csce": []}
    
    for problem in test_problems:
        print(f"\n{'='*60}")
        print(f"TESTING: {problem['name']}")
        print(f"{'='*60}")
        
        print("\n--- VANILLA APPROACH ---")
        start_time = time.time()
        try:
            vanilla_completion = client.complete(
                system=VANILLA_SYSTEM,
                user=problem['prompt'],
                max_tokens=1000
            )
            vanilla_time = time.time() - start_time
            vanilla_code = _strip_markdown_enhanced(vanilla_completion.text)
            
            print(f"Generated in {vanilla_time:.2f}s")
            print(f"Code length: {len(vanilla_code)} chars")
            print("Code preview:")
            print(vanilla_code[:200] + "..." if len(vanilla_code) > 200 else vanilla_code)
            
            results["vanilla"].append({
                "problem": problem['name'],
                "code": vanilla_code,
                "time": vanilla_time,
                "success": len(vanilla_code) > 10
            })
            
        except Exception as e:
            print(f"Vanilla failed: {e}")
            results["vanilla"].append({
                "problem": problem['name'],
                "code": "",
                "time": 0,
                "success": False
            })
        
        print("\n--- SIMPLIFIED CSCE APPROACH ---")
        start_time = time.time()
        try:
            csce_completion = client.complete(
                system=SIMPLIFIED_CSCE_SYSTEM,
                user=problem['prompt'],
                max_tokens=1000
            )
            csce_time = time.time() - start_time
            csce_code = _strip_markdown_enhanced(csce_completion.text)
            
            print(f"Generated in {csce_time:.2f}s")
            print(f"Code length: {len(csce_code)} chars")
            print("Code preview:")
            print(csce_code[:200] + "..." if len(csce_code) > 200 else csce_code)
            
            has_steps = "STEPS:" in csce_code or "# PLAN" in csce_code or "# THINK" in csce_code
            print(f"✓ Structured thinking found: {has_steps}")
            
            results["simplified_csce"].append({
                "problem": problem['name'],
                "code": csce_code,
                "time": csce_time,
                "success": len(csce_code) > 10,
                "structured": has_steps
            })
            
        except Exception as e:
            print(f"Simplified CSCE failed: {e}")
            results["simplified_csce"].append({
                "problem": problem['name'],
                "code": "",
                "time": 0,
                "success": False,
                "structured": False
            })
    
    print(f"\n{'='*60}")
    print("SUMMARY RESULTS")
    print(f"{'='*60}")
    
    vanilla_success = sum(1 for r in results["vanilla"] if r["success"])
    csce_success = sum(1 for r in results["simplified_csce"] if r["success"])
    vanilla_avg_time = sum(r["time"] for r in results["vanilla"]) / len(results["vanilla"])
    csce_avg_time = sum(r["time"] for r in results["simplified_csce"]) / len(results["simplified_csce"])
    
    print(f"Vanilla Success Rate: {vanilla_success}/{len(test_problems)} ({vanilla_success/len(test_problems)*100:.1f}%)")
    print(f"Simplified CSCE Success Rate: {csce_success}/{len(test_problems)} ({csce_success/len(test_problems)*100:.1f}%)")
    print(f"Vanilla Avg Time: {vanilla_avg_time:.2f}s")
    print(f"Simplified CSCE Avg Time: {csce_avg_time:.2f}s")
    
    structured_count = sum(1 for r in results["simplified_csce"] if r.get("structured", False))
    print(f"CSCE Structured Responses: {structured_count}/{len(test_problems)}")
    
    return results

if __name__ == "__main__":
    results = test_simplified_csce()
    
    import json
    with open("simplified_csce_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to simplified_csce_results.json")
