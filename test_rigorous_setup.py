"""
Test the rigorous evaluation setup
"""

import sys
import os
sys.path.append('.')
from rigorous_csce_evaluation import RigorousCSCEEvaluator

def test_setup():
    """Test that the rigorous evaluation can be initialized"""
    
    api_key = os.getenv('OPENAI_API')
    if not api_key:
        print("No API key available - testing with mock setup")
        return False
    
    try:
        evaluator = RigorousCSCEEvaluator(api_key, models=['gpt-4o-mini'])
        tasks = evaluator.create_test_tasks()
        print(f'✓ Created {len(tasks)} test tasks')
        print(f'✓ Task types: {[t["type"] for t in tasks[:5]]}')
        print(f'✓ Sample task: {tasks[0]["prompt"][:100]}...')
        
        print(f'✓ Baseline payload: {evaluator.baseline_payload}')
        print(f'✓ CSCE grid size: {len(evaluator.csce_grid)}')
        print(f'✓ Ablations: {len(evaluator.ablations)}')
        print(f'✓ Controls: {len(evaluator.controls)}')
        
        return True
        
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = test_setup()
    print(f"\nSetup test: {'PASSED' if success else 'FAILED'}")
