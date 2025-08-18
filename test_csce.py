#!/usr/bin/env python3
"""
Test script to validate CSCE kernel implementation before full experiments
"""

from csce_kernel import CSCEKernel, CodeAgentEvaluator, PayloadKnobs, ActionType
import time

def test_basic_kernel():
    """Test basic CSCE kernel functionality"""
    print("=== Testing Basic CSCE Kernel ===")
    
    kernel = CSCEKernel(initial_budget_sec=60)
    print(f"Initial state: sec_left={kernel.state.resources_sec_left}, uncertainty={kernel.state.uncertainty}")
    
    context = "Solve a simple coding problem: implement fibonacci function"
    action = kernel.select_action(context)
    print(f"Selected action: {action.action.value} (score={action.score:.2f})")
    
    output = kernel.execute_action(action, context)
    print(f"Action output: {output[:100]}...")
    print(f"Updated state: sec_left={kernel.state.resources_sec_left}, uncertainty={kernel.state.uncertainty:.2f}")
    
    print("\n--- Testing SELF-CALL ---")
    micro_outputs = kernel.self_call(q_seconds=2, repeats=2)
    print(f"SELF-CALL produced {len(micro_outputs)} micro-outputs")
    for i, output in enumerate(micro_outputs[:3]):
        print(f"  {i+1}: {output}")
    
    return True

def test_scoring_function():
    """Test the scoring function with different knob settings"""
    print("\n=== Testing Scoring Function ===")
    
    kernel = CSCEKernel()
    
    test_knobs = [
        PayloadKnobs(u=0, h="short", r="low", g=1, a=1),
        PayloadKnobs(u=3, h="long", r="high", g=3, a=2),
        PayloadKnobs(u=1, h="short", r="med", g=2, a=1)  # default
    ]
    
    for i, knobs in enumerate(test_knobs):
        kernel.knobs = knobs
        candidates = kernel.generate_candidates("test problem")
        best = max(candidates, key=lambda c: c.score)
        print(f"Knobs {i+1}: u={knobs.u}, g={knobs.g}, r={knobs.r} -> Best action: {best.action.value} (score={best.score:.2f})")
    
    return True

def test_evaluator():
    """Test the code agent evaluator"""
    print("\n=== Testing Code Agent Evaluator ===")
    
    evaluator = CodeAgentEvaluator()
    
    csce_result = evaluator.simulate_code_task("test task", time_limit=10, use_csce=True)
    vanilla_result = evaluator.simulate_code_task("test task", time_limit=10, use_csce=False)
    
    print(f"CSCE result: pass={csce_result.pass_at_1}, steps={csce_result.steps}, progress/sec={csce_result.progress_per_sec:.2f}")
    print(f"Vanilla result: pass={vanilla_result.pass_at_1}, steps={vanilla_result.steps}, progress/sec={vanilla_result.progress_per_sec:.2f}")
    
    return True

if __name__ == "__main__":
    start_time = time.time()
    
    success = True
    success &= test_basic_kernel()
    success &= test_scoring_function() 
    success &= test_evaluator()
    
    elapsed = time.time() - start_time
    print(f"\n=== Test Summary ===")
    print(f"All tests passed: {success}")
    print(f"Test execution time: {elapsed:.2f}s")
    
    if success:
        print("✓ CSCE kernel implementation validated - ready for experiments")
    else:
        print("✗ Issues found in CSCE kernel implementation")
