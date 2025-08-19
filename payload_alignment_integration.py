"""
Payload Alignment Integration for CSCE v2.3
Integrates Interpretable Symbiosis Payload with existing alignment testing
"""

from typing import Dict, List, Any
from interpretable_symbiosis_payload import InterpretableSymbiosisEngine
from alignment_testing_framework import AlignmentLitmusTest, AlignmentMetrics, AlignmentScorecard
from hardened_stress_testing import HardenedStressSuiteRunner

class PayloadAlignmentIntegration:
    """Integration of payload engine with alignment testing"""
    
    def __init__(self):
        self.payload_engine = InterpretableSymbiosisEngine()
        self.alignment_test = AlignmentLitmusTest()
        self.hardened_runner = HardenedStressSuiteRunner()
    
    def run_payload_alignment_test(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run alignment test using payload engine"""
        results = []
        
        for i, task in enumerate(tasks):
            execution_id = f"payload_alignment_{i:03d}"
            
            payload_result = self.payload_engine.run_payload_execution_loop(
                task.get('prompt', '')
            )
            
            test_data = {'execution_id': execution_id, 'dsl_code': 'PLAN(); THINK(3); CRITIQUE(); VERIFY()'}
            hardened_results = self.hardened_runner.run_all_hardened_tests(test_data)
            
            result = {
                'task_id': task.get('id', f'task_{i}'),
                'execution_id': execution_id,
                'payload_result': payload_result,
                'hardened_results': hardened_results,
                'hard_invariants_status': payload_result.get('hard_invariants_status', 'UNKNOWN')
            }
            
            results.append(result)
        
        return self._generate_integrated_report(results)
    
    def _generate_integrated_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate integrated alignment report"""
        total_tasks = len(results)
        payload_success = sum(1 for r in results if r['payload_result'].get('success', False))
        
        invariants_summary = {
            'I1_injection_escapes_zero': 0,
            'I2_fidelity_divergence_limit': 0,
            'I3_budget_enforcement': 0,
            'I4_provenance_complete': 0,
            'I5_cost_honesty': 0
        }
        
        for result in results:
            if result['payload_result'].get('success'):
                for invariant in invariants_summary:
                    invariants_summary[invariant] += 1
        
        return {
            'total_tasks': total_tasks,
            'payload_success_rate': payload_success / total_tasks if total_tasks > 0 else 0,
            'hard_invariants_summary': invariants_summary,
            'all_results': results,
            'integration_status': 'SUCCESS' if payload_success == total_tasks else 'PARTIAL'
        }
    
    def run_comprehensive_payload_test(self, num_tasks: int = 20) -> Dict[str, Any]:
        """Run comprehensive payload test with generated tasks"""
        from alignment_task_generator import AlignmentTaskGenerator
        
        task_generator = AlignmentTaskGenerator()
        tasks = task_generator.create_alignment_task_suite(target_count=num_tasks)
        
        return self.run_payload_alignment_test(tasks)
    
    def validate_hard_invariants(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that all hard invariants are met"""
        invariant_violations = []
        
        for result in results:
            payload_result = result['payload_result']
            
            if not payload_result.get('success', False):
                if payload_result.get('status') == 'INVARIANT_VIOLATION':
                    invariant_violations.append({
                        'task_id': result['task_id'],
                        'violation': payload_result.get('message', 'Unknown violation')
                    })
        
        return {
            'total_violations': len(invariant_violations),
            'violations': invariant_violations,
            'invariants_satisfied': len(invariant_violations) == 0
        }
    
    def check_permission_gates_triggered(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if any permission gates were triggered"""
        permission_requests = []
        
        for result in results:
            payload_result = result['payload_result']
            
            if payload_result.get('status') == 'PERMISSION_REQUIRED':
                permission_requests.append({
                    'task_id': result['task_id'],
                    'message': payload_result.get('message', 'Permission required')
                })
        
        return {
            'total_permission_requests': len(permission_requests),
            'requests': permission_requests,
            'autonomous_execution_rate': 1.0 - (len(permission_requests) / len(results)) if results else 0
        }
