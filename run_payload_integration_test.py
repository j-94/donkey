#!/usr/bin/env python3
"""
Test runner for Interpretable Symbiosis Payload integration
"""

import json
import time
from payload_alignment_integration import PayloadAlignmentIntegration
from alignment_task_generator import AlignmentTaskGenerator

def run_payload_integration_test():
    """Run comprehensive payload integration test"""
    print("🚀 Running Interpretable Symbiosis Payload Integration Test")
    print("=" * 70)
    
    start_time = time.time()
    
    task_generator = AlignmentTaskGenerator()
    tasks = task_generator.create_alignment_task_suite(target_count=20)
    
    integration = PayloadAlignmentIntegration()
    results = integration.run_payload_alignment_test(tasks)
    
    print(f"✅ Integration Status: {results['integration_status']}")
    print(f"⏱️  Duration: {time.time() - start_time:.2f}s")
    print(f"📊 Payload Success Rate: {results['payload_success_rate']:.1%}")
    
    print("\n🛡️ Hard Invariants Summary:")
    for invariant, count in results['hard_invariants_summary'].items():
        success_rate = count / results['total_tasks'] if results['total_tasks'] > 0 else 0
        status_icon = "✅" if success_rate == 1.0 else "❌"
        print(f"   {status_icon} {invariant}: {success_rate:.1%} ({count}/{results['total_tasks']})")
    
    invariant_validation = integration.validate_hard_invariants(results['all_results'])
    permission_analysis = integration.check_permission_gates_triggered(results['all_results'])
    
    print(f"\n🔒 Invariant Violations: {invariant_validation['total_violations']}")
    print(f"🚪 Permission Requests: {permission_analysis['total_permission_requests']}")
    print(f"🤖 Autonomous Execution Rate: {permission_analysis['autonomous_execution_rate']:.1%}")
    
    if invariant_validation['invariants_satisfied']:
        print("\n🎉 ALL HARD INVARIANTS SATISFIED - PAYLOAD INTEGRATION SUCCESS")
    else:
        print("\n🚨 HARD INVARIANT VIOLATIONS DETECTED - REVIEW REQUIRED")
        for violation in invariant_validation['violations']:
            print(f"   ❌ Task {violation['task_id']}: {violation['violation']}")
    
    with open('payload_integration_test_results.json', 'w') as f:
        json.dump({
            'integration_results': results,
            'invariant_validation': invariant_validation,
            'permission_analysis': permission_analysis,
            'test_duration': time.time() - start_time
        }, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: payload_integration_test_results.json")
    
    return results

def run_minimal_payload_test():
    """Run minimal payload test for quick validation"""
    print("🔬 Running Minimal Payload Test")
    print("=" * 40)
    
    from interpretable_symbiosis_payload import InterpretableSymbiosisEngine
    
    engine = InterpretableSymbiosisEngine()
    
    test_brief = "Analyze log data and generate a summary report"
    
    try:
        result = engine.run_payload_execution_loop(test_brief)
        
        if result['success']:
            print("✅ Payload execution successful")
            print(f"📋 Hard invariants status: {result.get('hard_invariants_status', 'UNKNOWN')}")
            
            if result.get('upgrade_proposals'):
                print(f"🔄 Upgrade proposals: {len(result['upgrade_proposals'])}")
            
            return True
        else:
            print(f"❌ Payload execution failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"💥 Payload test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Payload Integration Tests...\n")
    
    minimal_success = run_minimal_payload_test()
    print()
    
    if minimal_success:
        results = run_payload_integration_test()
    else:
        print("❌ Minimal test failed - skipping full integration test")
