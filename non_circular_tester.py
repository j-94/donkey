"""
Non-circular real-world CSCE tester with proper model calls and test isolation
"""

import sys
import json
import time
import traceback
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

sys.path.append('/home/ubuntu/human-eval')
from human_eval.data import read_problems

from model_client import ModelClient, MockClient, OpenAIClient
from vanilla_generator import VanillaGenerator, VANILLA_SYSTEM_PROMPT
from csce_generator import CSCEPolicyGenerator, CSCE_SYSTEM_PROMPT
from csce_kernel import PayloadKnobs
from safe_executor import SafeCodeExecutor

@dataclass
class TestResult:
    task_id: str
    approach: str  # "vanilla" or "csce"
    prompt: str
    generated_code: str
    pass_at_1: bool
    execution_time: float
    model_latency: float
    steps: int = 1  # 1 for vanilla, variable for CSCE
    uncertainty: float = 0.0  # 0 for vanilla, variable for CSCE
    error_message: str = ""
    compile_pass: bool = True  # Whether code compiles/imports successfully
    entry_point_error: bool = False  # Whether expected entry point is missing

class NonCircularCSCETester:
    """Non-circular tester that uses real model calls and proper test isolation"""
    
    def __init__(self, model_client: ModelClient):
        self.model_client = model_client
        self.executor = SafeCodeExecutor(timeout_seconds=10)
        
        self.vanilla_generator = VanillaGenerator(model_client, VANILLA_SYSTEM_PROMPT)
        
        default_knobs = PayloadKnobs(u=0, h="short", r="low", g=1, a=1)
        self.csce_generator = CSCEPolicyGenerator(model_client, CSCE_SYSTEM_PROMPT, default_knobs)
    
    def test_humaneval_problem(self, task_id: str, problem: Dict[str, Any]) -> List[TestResult]:
        """Test both vanilla and CSCE approaches on a single HumanEval problem"""
        results = []
        
        prompt = problem['prompt']
        test_code = problem['test']
        entry_point = problem['entry_point']
        
        print(f"  Testing vanilla on {task_id}...")
        vanilla_result = self._test_approach(
            task_id=task_id,
            approach="vanilla",
            prompt=prompt,
            test_code=test_code,
            entry_point=entry_point
        )
        results.append(vanilla_result)
        
        print(f"  Testing CSCE on {task_id}...")
        csce_result = self._test_approach(
            task_id=task_id,
            approach="csce",
            prompt=prompt,
            test_code=test_code,
            entry_point=entry_point
        )
        results.append(csce_result)
        
        return results
    
    def test_mbpp_problem(self, problem: Dict[str, Any]) -> List[TestResult]:
        """Test both approaches on a single MBPP problem"""
        results = []
        
        task_id = f"MBPP_{problem['task_id']}"
        prompt = problem['prompt']
        test_assertions = "\n".join(problem['test_list'])
        
        entry_point = self._extract_function_name_from_tests(test_assertions)
        if not entry_point:
            print(f"  Warning: Could not extract function name from {task_id}")
            return results
        
        print(f"  Testing vanilla on {task_id}...")
        vanilla_result = self._test_approach(
            task_id=task_id,
            approach="vanilla",
            prompt=prompt,
            test_code=test_assertions,
            entry_point=entry_point
        )
        results.append(vanilla_result)
        
        print(f"  Testing CSCE on {task_id}...")
        csce_result = self._test_approach(
            task_id=task_id,
            approach="csce",
            prompt=prompt,
            test_code=test_assertions,
            entry_point=entry_point
        )
        results.append(csce_result)
        
        return results
    
    def _test_approach(self, task_id: str, approach: str, prompt: str, test_code: str, entry_point: str) -> TestResult:
        """Test a single approach on a problem"""
        try:
            start_time = time.time()
            
            arity = self._infer_arity(entry_point, test_code)
            
            if approach == "vanilla":
                generated_code, model_latency = self.vanilla_generator.generate(
                    prompt, seconds_budget=30, entry_point=entry_point, arity=arity
                )
                steps, uncertainty = 1, 0.0
            else:  # CSCE
                generated_code, steps, uncertainty, model_latency = self.csce_generator.generate(
                    prompt, seconds_budget=30, entry_point=entry_point, arity=arity
                )
            
            success, stdout, stderr, exec_time, compile_pass, entry_point_error = self.executor.run(
                candidate_code=generated_code,
                test_code=test_code,
                entry_point=entry_point
            )
            
            total_time = time.time() - start_time
            
            return TestResult(
                task_id=task_id,
                approach=approach,
                prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                generated_code=generated_code,
                pass_at_1=success,
                execution_time=total_time,
                model_latency=model_latency,
                steps=steps,
                uncertainty=uncertainty,
                error_message=stderr if not success else "",
                compile_pass=compile_pass,
                entry_point_error=entry_point_error
            )
            
        except Exception as e:
            return TestResult(
                task_id=task_id,
                approach=approach,
                prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                generated_code="",
                pass_at_1=False,
                execution_time=0.0,
                model_latency=0.0,
                steps=0,
                uncertainty=1.0,
                error_message=f"Generation failed: {str(e)}"
            )
    
    def _extract_function_name_from_tests(self, test_code: str) -> str:
        """Extract function name from test assertions using improved regex"""
        import re
        
        for line in test_code.split('\n'):
            match = re.search(r'assert\s+([A-Za-z_]\w*)\s*\(', line)
            if match:
                return match.group(1)
        
        matches = re.findall(r'(\w+)\s*\(', test_code)
        if matches:
            builtin_functions = {'assert', 'set', 'len', 'str', 'int', 'float', 'list', 'tuple', 'dict', 'bool', 'abs', 'max', 'min', 'sum', 'sorted', 'reversed'}
            function_names = [m for m in matches if m not in builtin_functions]
            if function_names:
                return function_names[0]
        
        return ""
    
    def _infer_arity(self, fn_name: str, test_code: str) -> int:
        """Infer function arity from test calls"""
        import re
        
        for line in test_code.split('\n'):
            match = re.search(rf'{re.escape(fn_name)}\((.*?)\)', line)
            if match:
                args_str = match.group(1)
                args = [a.strip() for a in re.split(r',(?![^()]*\))', args_str) if a.strip()]
                return max(1, len(args))
        
        return 2  # fallback
    
    def run_evaluation(self, num_humaneval: int = 5, num_mbpp: int = 5) -> Dict[str, Any]:
        """Run complete evaluation on both datasets"""
        print("=== NON-CIRCULAR CSCE EVALUATION ===")
        print(f"Testing {num_humaneval} HumanEval + {num_mbpp} MBPP problems")
        print(f"Model client: {type(self.model_client).__name__}")
        
        all_results = []
        
        if num_humaneval > 0:
            print(f"\nTesting {num_humaneval} HumanEval problems...")
            problems = read_problems()
            for i, (task_id, problem) in enumerate(list(problems.items())[:num_humaneval]):
                print(f"Problem {i+1}/{num_humaneval}: {task_id}")
                results = self.test_humaneval_problem(task_id, problem)
                all_results.extend(results)
        
        if num_mbpp > 0:
            print(f"\nTesting {num_mbpp} MBPP problems...")
            with open('/home/ubuntu/google-research/mbpp/sanitized-mbpp.json', 'r') as f:
                mbpp_data = json.load(f)
            
            for i, problem in enumerate(mbpp_data[:num_mbpp]):
                print(f"Problem {i+1}/{num_mbpp}: MBPP_{problem['task_id']}")
                results = self.test_mbpp_problem(problem)
                all_results.extend(results)
        
        analysis = self._analyze_results(all_results)
        
        return {
            'results': [asdict(r) for r in all_results],
            'analysis': analysis
        }
    
    def _analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze and compare vanilla vs CSCE results"""
        vanilla_results = [r for r in results if r.approach == "vanilla"]
        csce_results = [r for r in results if r.approach == "csce"]
        
        def compute_stats(results_list):
            if not results_list:
                return {}
            
            pass_count = sum(1 for r in results_list if r.pass_at_1)
            total_count = len(results_list)
            
            return {
                'pass_at_1': pass_count / total_count if total_count > 0 else 0.0,
                'total_problems': total_count,
                'passed_problems': pass_count,
                'avg_model_latency': sum(r.model_latency for r in results_list) / total_count,
                'avg_execution_time': sum(r.execution_time for r in results_list) / total_count,
                'avg_steps': sum(r.steps for r in results_list) / total_count,
                'avg_uncertainty': sum(r.uncertainty for r in results_list) / total_count
            }
        
        vanilla_stats = compute_stats(vanilla_results)
        csce_stats = compute_stats(csce_results)
        
        return {
            'vanilla': vanilla_stats,
            'csce': csce_stats,
            'comparison': {
                'pass_at_1_improvement': csce_stats.get('pass_at_1', 0) - vanilla_stats.get('pass_at_1', 0),
                'latency_overhead': csce_stats.get('avg_model_latency', 0) - vanilla_stats.get('avg_model_latency', 0),
                'avg_steps_csce': csce_stats.get('avg_steps', 0)
            }
        }

def main():
    """Main function to run non-circular evaluation"""
    
    print("Initializing with MockClient for testing...")
    client = MockClient(mock_latency=0.1)  # Fast mock for testing
    
    
    tester = NonCircularCSCETester(client)
    
    results = tester.run_evaluation(num_humaneval=2, num_mbpp=2)
    
    with open('/home/ubuntu/non_circular_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    analysis = results['analysis']
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Vanilla pass@1: {analysis['vanilla']['pass_at_1']:.1%}")
    print(f"CSCE pass@1: {analysis['csce']['pass_at_1']:.1%}")
    print(f"Improvement: {analysis['comparison']['pass_at_1_improvement']:+.1%}")
    print(f"CSCE avg steps: {analysis['csce']['avg_steps']:.1f}")
    print(f"Model latency overhead: {analysis['comparison']['latency_overhead']:.3f}s")
    
    print(f"\nResults saved to non_circular_results.json")

if __name__ == "__main__":
    main()
