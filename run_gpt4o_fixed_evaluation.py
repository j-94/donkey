"""
Run GPT-4o evaluation with fixed system prompts to prevent markdown formatting
"""

import os
import json
from model_client import OpenAIClient
from non_circular_tester import NonCircularCSCETester

def main():
    """Run evaluation with GPT-4o and fixed prompts"""
    print("=== GPT-4o EVALUATION (FIXED PROMPTS) ===")
    
    api_key = os.getenv('OPENAI_API')
    if not api_key:
        print("ERROR: OPENAI_API environment variable not set")
        return
    
    print(f"Using OpenAI API key: {api_key[:8]}...")
    
    client = OpenAIClient(model="gpt-4o", api_key=api_key)
    print(f"Model: {client.model}")
    
    tester = NonCircularCSCETester(client)
    
    print("\nRunning evaluation on 3 HumanEval + 3 MBPP problems...")
    print("This will make real API calls with fixed prompts to prevent markdown formatting...")
    
    results = tester.run_evaluation(num_humaneval=3, num_mbpp=3)
    
    with open('/home/ubuntu/gpt4o_fixed_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    analysis = results['analysis']
    print("\n=== GPT-4o FIXED EVALUATION RESULTS ===")
    print(f"Vanilla Results:")
    print(f"  Pass@1: {analysis['vanilla']['pass_at_1']:.1%}")
    print(f"  Avg model latency: {analysis['vanilla']['avg_model_latency']:.3f}s")
    print(f"  Avg steps: {analysis['vanilla']['avg_steps']:.1f}")
    
    print(f"\nCSCE Results:")
    print(f"  Pass@1: {analysis['csce']['pass_at_1']:.1%}")
    print(f"  Avg model latency: {analysis['csce']['avg_model_latency']:.3f}s")
    print(f"  Avg steps: {analysis['csce']['avg_steps']:.1f}")
    print(f"  Avg uncertainty: {analysis['csce']['avg_uncertainty']:.3f}")
    
    print(f"\nComparison:")
    print(f"  Pass@1 improvement: {analysis['comparison']['pass_at_1_improvement']:+.1%}")
    print(f"  Latency overhead: {analysis['comparison']['latency_overhead']:+.3f}s")
    
    print(f"\nExample Results:")
    for i, result in enumerate(results['results'][:4]):  # Show first 4
        status = "✅ PASS" if result['pass_at_1'] else "❌ FAIL"
        print(f"  {result['task_id']} ({result['approach']}): {status} - {result['model_latency']:.3f}s")
    
    print(f"\nResults saved to gpt4o_fixed_results.json")
    
    total_latency = sum(r['model_latency'] for r in results['results'])
    print(f"\nVerification:")
    print(f"  Total model latency: {total_latency:.3f}s")
    print(f"  Real API calls: {'✅ YES' if total_latency > 1.0 else '⚠️  Suspiciously fast'}")

if __name__ == "__main__":
    main()
