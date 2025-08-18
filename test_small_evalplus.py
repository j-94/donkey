"""
Test the updated CSCE v2.3 system on a small subset of EvalPlus problems
"""

import os
from evalplus.sanitize import get_human_eval_plus
from run_evalplus_csce import call_model_with, coerce_function_name, _strip_markdown_enhanced

def test_small_subset():
    """Test on first 3 HumanEval+ problems"""
    print("=== Testing CSCE v2.3 on Small EvalPlus Subset ===")
    
    humaneval_plus = get_human_eval_plus()
    test_problems = dict(list(humaneval_plus.items())[:3])
    
    print(f"Testing on {len(test_problems)} problems:")
    for task_id in test_problems.keys():
        print(f"  - {task_id}")
    
    print("\n=== VANILLA RESULTS ===")
    vanilla_results = []
    for task_id, task_data in test_problems.items():
        print(f"\nTesting {task_id} with vanilla...")
        try:
            solution = call_model_with("vanilla", task_data["prompt"], task_data.get("entry_point"))
            solution = coerce_function_name(solution, task_data["entry_point"])
            print(f"Generated solution length: {len(solution)} chars")
            vanilla_results.append({"task_id": task_id, "solution": solution})
        except Exception as e:
            print(f"Error: {e}")
            vanilla_results.append({"task_id": task_id, "solution": f"# Error: {e}"})
    
    print("\n=== CSCE v2.3 RESULTS ===")
    csce_results = []
    for task_id, task_data in test_problems.items():
        print(f"\nTesting {task_id} with CSCE v2.3...")
        try:
            solution = call_model_with("csce", task_data["prompt"], task_data.get("entry_point"))
            solution = coerce_function_name(solution, task_data["entry_point"])
            print(f"Generated solution length: {len(solution)} chars")
            print("First few lines:")
            print('\n'.join(solution.split('\n')[:3]))
            csce_results.append({"task_id": task_id, "solution": solution})
        except Exception as e:
            print(f"Error: {e}")
            csce_results.append({"task_id": task_id, "solution": f"# Error: {e}"})
    
    print(f"\n=== SUMMARY ===")
    print(f"Vanilla: {len([r for r in vanilla_results if not r['solution'].startswith('# Error')])} successful")
    print(f"CSCE v2.3: {len([r for r in csce_results if not r['solution'].startswith('# Error')])} successful")
    print("Small subset test complete!")

if __name__ == "__main__":
    test_small_subset()
