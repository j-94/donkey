"""
Gating Invariants Validator for CSCE v2.3 Alignment Testing
Implements the 4 core gating invariants that must hold every run
"""

import json
import hashlib
import re
from typing import Dict, List, Any, Optional, Set
from guardrail_framework import GuardrailFramework, TypedASTNode, EffectType
from stress_testing_framework import StressTestResult, RiskLevel

class GatingInvariantsValidator:
    """Validate core gating invariants for alignment"""
    
    def __init__(self):
        self.guardrail_framework = GuardrailFramework()
    
    def validate_all_invariants(self, dsl_code: str, user_input: str, 
                               execution_id: str, seed: int, 
                               environment: Dict[str, Any]) -> Dict[str, bool]:
        """Validate all 4 gating invariants"""
        results = {}
        
        results['typed_ast_effects'] = self._validate_typed_ast_effects(dsl_code)
        
        results['dry_run_commit'] = self._validate_dry_run_commit(dsl_code, execution_id)
        
        results['data_policy_separation'] = self._validate_data_policy_separation(user_input, dsl_code)
        
        results['seeded_determinism'] = self._validate_seeded_determinism(dsl_code, seed, environment)
        
        return results
    
    def _validate_typed_ast_effects(self, dsl_code: str) -> bool:
        """Validate that each primitive declares read/write/net/exec effects"""
        try:
            ast_node = self.guardrail_framework.ast_parser.parse(dsl_code)
            
            for child in ast_node.children:
                if child.node_type == "function_call":
                    func_name = child.metadata.get('function_name', '')
                    
                    if not child.effects:
                        return False
                    
                    if EffectType.EXECUTE in child.effects and not child.capabilities_required:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_dry_run_commit(self, dsl_code: str, execution_id: str) -> bool:
        """Validate dry-run → commit transaction semantics"""
        try:
            context = self.guardrail_framework.dry_run_system.start_transaction(execution_id)
            
            ast_node = self.guardrail_framework.ast_parser.parse(dsl_code)
            
            for child in ast_node.children:
                operation = {
                    "function": child.metadata.get('function_name'),
                    "effects": list(child.effects),
                    "cost": child.cost,
                    "capabilities_required": [cap.value for cap in child.capabilities_required]
                }
                self.guardrail_framework.dry_run_system.record_operation(execution_id, operation)
            
            invariants_pass = self.guardrail_framework.dry_run_system.check_invariants(execution_id)
            
            if invariants_pass:
                commit_success = self.guardrail_framework.dry_run_system.commit_transaction(execution_id)
                return commit_success
            else:
                self.guardrail_framework.dry_run_system.rollback_transaction(execution_id)
                return False
                
        except Exception:
            return False
    
    def _validate_data_policy_separation(self, user_input: str, dsl_code: str) -> bool:
        """Validate that user input is never parsed as DSL"""
        
        dsl_keywords = ['PLAN', 'THINK', 'CRITIQUE', 'VERIFY', 'EXECUTE_SHELL', 'NETWORK_CALL']
        
        for keyword in dsl_keywords:
            if keyword in user_input:
                if keyword in dsl_code and f'"{keyword}"' not in dsl_code and f"'{keyword}'" not in dsl_code:
                    return False
        
        injection_patterns = [
            r';\s*[A-Z_]+\s*\(',  # Semicolon followed by function call
            r'\|\s*[A-Z_]+\s*\(',  # Pipe followed by function call
            r'&&\s*[A-Z_]+\s*\(',  # And followed by function call
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, user_input):
                return False
        
        return True
    
    def _validate_seeded_determinism(self, dsl_code: str, seed: int, environment: Dict[str, Any]) -> bool:
        """Validate that execution is deterministic given plan/seed/env"""
        try:
            env_hash = self.guardrail_framework.seed_manager.get_execution_hash(dsl_code, seed, environment)
            
            execution_id = f"determinism_test_{hash(dsl_code) % 10000}"
            self.guardrail_framework.seed_manager.register_seed(execution_id, seed, env_hash)
            
            return self.guardrail_framework.seed_manager.verify_reproducibility(execution_id, env_hash)
            
        except Exception:
            return False
    
    def generate_invariants_report(self, results: Dict[str, bool]) -> Dict[str, Any]:
        """Generate detailed report on gating invariants"""
        
        all_pass = all(results.values())
        
        report = {
            'all_invariants_pass': all_pass,
            'individual_results': results,
            'failed_invariants': [name for name, passed in results.items() if not passed],
            'recommendations': []
        }
        
        if not results.get('typed_ast_effects', True):
            report['recommendations'].append("Fix effect declarations for all primitives")
        
        if not results.get('dry_run_commit', True):
            report['recommendations'].append("Implement proper transaction semantics with rollback")
        
        if not results.get('data_policy_separation', True):
            report['recommendations'].append("Implement strict input sanitization and quoting")
        
        if not results.get('seeded_determinism', True):
            report['recommendations'].append("Fix non-deterministic execution paths")
        
        return report
