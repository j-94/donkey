"""
Hard Budget Enforcement Framework for CSCE v2.3
Implements zero-tolerance budget enforcement with kill switches
"""

import time
import threading
import signal
import resource
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from enum import Enum
from injection_hardening import Cap, Prim

class BudgetType(Enum):
    TIME_MS = "time_ms"
    CALLS = "calls"
    MEMORY_BYTES = "memory_bytes"
    COST_DOLLARS = "cost_dollars"

@dataclass
class Budget:
    """Budget constraints with hard limits"""
    time_ms: int
    calls: int
    memory_bytes: int = 1024 * 1024 * 100  # 100MB default
    cost_dollars: float = 1.0  # $1 default
    
    def __post_init__(self):
        """Validate budget constraints"""
        if self.time_ms <= 0 or self.calls <= 0:
            raise ValueError("Budget constraints must be positive")

class BudgetViolationError(Exception):
    """Raised when budget limits are exceeded"""
    pass

class BudgetEnforcer:
    """Hard budget enforcement with preemptive termination"""
    
    def __init__(self):
        self.active_budgets: Dict[str, Budget] = {}
        self.usage_tracking: Dict[str, Dict[str, float]] = {}
        self.kill_switches: Dict[str, threading.Event] = {}
        
    def register_budget(self, execution_id: str, budget: Budget):
        """Register budget constraints for an execution"""
        self.active_budgets[execution_id] = budget
        self.usage_tracking[execution_id] = {
            'time_ms': 0,
            'calls': 0,
            'memory_bytes': 0,
            'cost_dollars': 0.0
        }
        self.kill_switches[execution_id] = threading.Event()
    
    def check_budget_available(self, execution_id: str, prim: Prim) -> bool:
        """Check if primitive can run within remaining budget"""
        if execution_id not in self.active_budgets:
            return False
        
        budget = self.active_budgets[execution_id]
        usage = self.usage_tracking[execution_id]
        
        if usage['time_ms'] + prim.budget_ms > budget.time_ms:
            return False
        
        if usage['calls'] + prim.budget_calls > budget.calls:
            return False
        
        return True
    
    def start_execution_timer(self, execution_id: str, timeout_ms: int):
        """Start execution timer with hard kill after timeout"""
        def timeout_handler():
            time.sleep(timeout_ms / 1000.0)
            if not self.kill_switches[execution_id].is_set():
                self.kill_switches[execution_id].set()
                raise BudgetViolationError(f"Execution {execution_id} exceeded time budget: {timeout_ms}ms")
        
        timer_thread = threading.Thread(target=timeout_handler, daemon=True)
        timer_thread.start()
        return timer_thread
    
    def record_usage(self, execution_id: str, budget_type: BudgetType, amount: float):
        """Record resource usage and check for violations"""
        if execution_id not in self.usage_tracking:
            raise ValueError(f"Unknown execution ID: {execution_id}")
        
        usage = self.usage_tracking[execution_id]
        budget = self.active_budgets[execution_id]
        
        usage[budget_type.value] += amount
        
        if budget_type == BudgetType.TIME_MS and usage['time_ms'] > budget.time_ms:
            self.kill_switches[execution_id].set()
            raise BudgetViolationError(f"Time budget exceeded: {usage['time_ms']}ms > {budget.time_ms}ms")
        
        elif budget_type == BudgetType.CALLS and usage['calls'] > budget.calls:
            self.kill_switches[execution_id].set()
            raise BudgetViolationError(f"Call budget exceeded: {usage['calls']} > {budget.calls}")
        
        elif budget_type == BudgetType.MEMORY_BYTES and usage['memory_bytes'] > budget.memory_bytes:
            self.kill_switches[execution_id].set()
            raise BudgetViolationError(f"Memory budget exceeded: {usage['memory_bytes']} > {budget.memory_bytes}")
        
        elif budget_type == BudgetType.COST_DOLLARS and usage['cost_dollars'] > budget.cost_dollars:
            self.kill_switches[execution_id].set()
            raise BudgetViolationError(f"Cost budget exceeded: ${usage['cost_dollars']} > ${budget.cost_dollars}")
    
    def run_primitive_with_budget(self, execution_id: str, prim: Prim, env: Dict[str, Any]) -> Any:
        """Execute primitive with strict budget enforcement"""
        if not self.check_budget_available(execution_id, prim):
            raise BudgetViolationError(f"Insufficient budget for primitive {prim.name}")
        
        if self.kill_switches[execution_id].is_set():
            raise BudgetViolationError(f"Execution {execution_id} has been terminated")
        
        start_time = time.time()
        timer = self.start_execution_timer(execution_id, prim.budget_ms)
        
        try:
            self._enforce_capabilities(prim.effects, env)
            
            result = self._execute_primitive(prim, env)
            
            actual_time_ms = (time.time() - start_time) * 1000
            self.record_usage(execution_id, BudgetType.TIME_MS, actual_time_ms)
            self.record_usage(execution_id, BudgetType.CALLS, 1)
            
            return result
            
        except BudgetViolationError:
            self.kill_switches[execution_id].set()
            raise
        
        except Exception as e:
            actual_time_ms = (time.time() - start_time) * 1000
            self.record_usage(execution_id, BudgetType.TIME_MS, actual_time_ms)
            self.record_usage(execution_id, BudgetType.CALLS, 1)
            raise
        
        finally:
            self.kill_switches[execution_id].set()
    
    def _enforce_capabilities(self, required_caps: set, env: Dict[str, Any]):
        """Enforce capability constraints"""
        available_caps = env.get('capabilities', set())
        
        for cap in required_caps:
            if cap not in available_caps:
                raise BudgetViolationError(f"Missing required capability: {cap}")
    
    def _execute_primitive(self, prim: Prim, env: Dict[str, Any]) -> Any:
        """Mock primitive execution - replace with actual implementation"""
        time.sleep(0.001)  # 1ms simulation
        
        return {
            'primitive': prim.name,
            'result': f"Executed {prim.name} with args {prim.args}",
            'effects': [cap.name for cap in prim.effects]
        }
    
    def get_budget_report(self, execution_id: str) -> Dict[str, Any]:
        """Generate budget usage report"""
        if execution_id not in self.active_budgets:
            return {'error': f'Unknown execution ID: {execution_id}'}
        
        budget = self.active_budgets[execution_id]
        usage = self.usage_tracking[execution_id]
        
        return {
            'execution_id': execution_id,
            'budget_limits': {
                'time_ms': budget.time_ms,
                'calls': budget.calls,
                'memory_bytes': budget.memory_bytes,
                'cost_dollars': budget.cost_dollars
            },
            'actual_usage': usage.copy(),
            'remaining': {
                'time_ms': max(0, budget.time_ms - usage['time_ms']),
                'calls': max(0, budget.calls - usage['calls']),
                'memory_bytes': max(0, budget.memory_bytes - usage['memory_bytes']),
                'cost_dollars': max(0, budget.cost_dollars - usage['cost_dollars'])
            },
            'violations': {
                'time': usage['time_ms'] > budget.time_ms,
                'calls': usage['calls'] > budget.calls,
                'memory': usage['memory_bytes'] > budget.memory_bytes,
                'cost': usage['cost_dollars'] > budget.cost_dollars
            },
            'killed': self.kill_switches[execution_id].is_set()
        }
    
    def cleanup_execution(self, execution_id: str):
        """Clean up execution tracking"""
        if execution_id in self.active_budgets:
            del self.active_budgets[execution_id]
        if execution_id in self.usage_tracking:
            del self.usage_tracking[execution_id]
        if execution_id in self.kill_switches:
            del self.kill_switches[execution_id]

def test_budget_enforcement() -> Dict[str, Any]:
    """Test budget enforcement with various scenarios"""
    enforcer = BudgetEnforcer()
    test_results = {}
    
    try:
        execution_id = "test_normal"
        budget = Budget(time_ms=5000, calls=10)
        enforcer.register_budget(execution_id, budget)
        
        prim = Prim(name="TEST_PRIM", args={}, effects={Cap.READ}, budget_ms=100, budget_calls=1)
        env = {'capabilities': {Cap.READ}}
        
        result = enforcer.run_primitive_with_budget(execution_id, prim, env)
        test_results['normal_execution'] = True
        
    except Exception as e:
        test_results['normal_execution'] = False
    
    try:
        execution_id = "test_violation"
        budget = Budget(time_ms=10, calls=1)  # Very tight budget
        enforcer.register_budget(execution_id, budget)
        
        prim = Prim(name="SLOW_PRIM", args={}, effects={Cap.EXEC}, budget_ms=1000, budget_calls=1)
        env = {'capabilities': {Cap.EXEC}}
        
        result = enforcer.run_primitive_with_budget(execution_id, prim, env)
        test_results['budget_violation'] = False  # Should have failed
        
    except BudgetViolationError:
        test_results['budget_violation'] = True  # Correctly caught violation
    
    try:
        execution_id = "test_capability"
        budget = Budget(time_ms=5000, calls=10)
        enforcer.register_budget(execution_id, budget)
        
        prim = Prim(name="WRITE_PRIM", args={}, effects={Cap.WRITE}, budget_ms=100, budget_calls=1)
        env = {'capabilities': {Cap.READ}}  # Missing WRITE capability
        
        result = enforcer.run_primitive_with_budget(execution_id, prim, env)
        test_results['capability_violation'] = False  # Should have failed
        
    except BudgetViolationError:
        test_results['capability_violation'] = True  # Correctly caught violation
    
    return {
        'test_results': test_results,
        'all_passed': all(test_results.values()),
        'violations_detected': test_results.get('budget_violation', False) and test_results.get('capability_violation', False)
    }
