"""
Run the final fixed evaluation with proper entry-point extraction, name-strict prompts, and detailed error analysis
"""

import os
import json
from model_client import OpenAIClient
from non_circular_tester import NonCircularCSCETester

def main():
    """Run final fixed evaluation with GPT-4o and proper entry point handling"""
    print("=== FINAL FIXED EVALUATION WITH PROPER ENTRY POINTS ===")
    
    api_key = os.getenv('OPENAI_API')
    if not api_key:
        print("ERROR: OPENAI_API environment variable not set")
        return
    
    print(f"Using OpenAI API key: {api_key[:8]}...")
    
    client = OpenAIClient(model="gpt-4o", api_key=api_key, temperature=0.2)
    print(f"Model: {client.model}, Temperature: 0.2")
    
    tester = NonCircularCSCETester(client)
    
    print("\nRunning evaluation on 3 HumanEval + 3 MBPP problems...")
    print("Using name-strict prompts with proper entry point extraction...")
    print("Temperature=0.2, Budget=30s, CSCE r1_q2 config")
    
    results = tester.run_evaluation(num_humaneval=3, num_mbpp=3)
    
    with open('/home/ubuntu/final_fixed_evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    analysis = results['analysis']
    print("\n=== FINAL FIXED EVALUATION RESULTS ===")
    
    vanilla_results = [r for r in results['results'] if r['approach'] == 'vanilla']
    csce_results = [r for r in results['results'] if r['approach'] == 'csce']
    
    def analyze_errors(results_list, approach_name):
        total = len(results_list)
        passed = sum(1 for r in results_list if r['pass_at_1'])
        compile_errors = sum(1 for r in results_list if not r['compile_pass'])
        entry_point_errors = sum(1 for r in results_list if r['entry_point_error'])
        logic_errors = sum(1 for r in results_list if r['compile_pass'] and not r['entry_point_error'] and not r['pass_at_1'])
        
        print(f"\n{approach_name} Error Breakdown:")
        print(f"  Total problems: {total}")
        print(f"  Passed: {passed} ({passed/total:.1%})")
        print(f"  Compile errors: {compile_errors} ({compile_errors/total:.1%})")
        print(f"  Entry point errors: {entry_point_errors} ({entry_point_errors/total:.1%})")
        print(f"  Logic errors: {logic_errors} ({logic_errors/total:.1%})")
        print(f"  Avg model latency: {sum(r['model_latency'] for r in results_list)/total:.3f}s")
        print(f"  Avg steps: {sum(r['steps'] for r in results_list)/total:.1f}")
        
        return {
            'pass_at_1': passed/total,
            'compile_errors': compile_errors/total,
            'entry_point_errors': entry_point_errors/total,
            'logic_errors': logic_errors/total
        }
    
    vanilla_breakdown = analyze_errors(vanilla_results, "Vanilla")
    csce_breakdown = analyze_errors(csce_results, "CSCE")
    
    print(f"\nComparison:")
    print(f"  Pass@1 improvement: {csce_breakdown['pass_at_1'] - vanilla_breakdown['pass_at_1']:+.1%}")
    print(f"  Compile error reduction: {vanilla_breakdown['compile_errors'] - csce_breakdown['compile_errors']:+.1%}")
    print(f"  Entry point error reduction: {vanilla_breakdown['entry_point_errors'] - csce_breakdown['entry_point_errors']:+.1%}")
    print(f"  Logic error change: {csce_breakdown['logic_errors'] - vanilla_breakdown['logic_errors']:+.1%}")
    
    print(f"\nDetailed Results by Problem:")
    for i, result in enumerate(results['results']):
        status = "✅ PASS" if result['pass_at_1'] else "❌ FAIL"
        error_type = ""
        if not result['pass_at_1']:
            if not result['compile_pass']:
                error_type = " (COMPILE)"
            elif result['entry_point_error']:
                error_type = " (ENTRY_POINT)"
            else:
                error_type = " (LOGIC)"
        
        print(f"  {result['task_id']} ({result['approach']}): {status}{error_type} - {result['model_latency']:.3f}s, {result['steps']} steps")
    
    print(f"\nResults saved to final_fixed_evaluation_results.json")
    
    total_latency = sum(r['model_latency'] for r in results['results'])
    print(f"\nVerification:")
    print(f"  Total model latency: {total_latency:.3f}s")
    print(f"  Real API calls: {'✅ YES' if total_latency > 1.0 else '⚠️  Suspiciously fast'}")
    
    print(f"\nExample Generated Code (first successful result):")
    for result in results['results']:
        if result['pass_at_1'] and result['generated_code']:
            print(f"Task: {result['task_id']} ({result['approach']})")
            print(f"Code:\n{result['generated_code'][:200]}...")
            break

if __name__ == "__main__":
    main()
