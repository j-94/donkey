"""
Cost Honesty Framework for CSCE v2.3
Implements expanded AST billing and macro cost transparency
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Any, Set, Optional
from injection_hardening import Prim, Cap

@dataclass
class CostBreakdown:
    """Detailed cost breakdown for primitives"""
    primitive_name: str
    declared_cost: float
    expanded_cost: float
    time_cost: float
    memory_cost: float
    network_cost: float
    compute_cost: float
    
    @property
    def cost_delta(self) -> float:
        """Calculate cost delta percentage"""
        if self.declared_cost == 0:
            return float('inf') if self.expanded_cost > 0 else 0
        return (self.expanded_cost - self.declared_cost) / self.declared_cost

@dataclass
class MacroDefinition:
    """Macro primitive definition with expansion rules"""
    name: str
    parameters: List[str]
    expansion: List[Prim]
    spec: str
    examples: List[Dict[str, Any]]
    safety_proof: str
    approvals: List[str]
    
    def is_approved(self) -> bool:
        """Check if macro has required approvals"""
        return len(self.approvals) >= 2

class CostHonestyEnforcer:
    """Enforce cost honesty through expanded AST billing"""
    
    def __init__(self):
        self.macro_registry: Dict[str, MacroDefinition] = {}
        self.cost_history: Dict[str, List[CostBreakdown]] = {}
        
        self.base_costs = {
            'READ': 0.1,
            'WRITE': 0.2,
            'NETWORK': 1.0,
            'EXECUTE': 0.5,
            'COMPUTE': 0.3
        }
    
    def register_macro(self, macro_def: MacroDefinition) -> bool:
        """Register new macro with approval requirements"""
        if not macro_def.is_approved():
            raise ValueError(f"Macro {macro_def.name} requires 2 approvals, has {len(macro_def.approvals)}")
        
        if not macro_def.spec or not macro_def.examples or not macro_def.safety_proof:
            raise ValueError(f"Macro {macro_def.name} missing required documentation")
        
        self.macro_registry[macro_def.name] = macro_def
        return True
    
    def is_macro(self, prim: Prim) -> bool:
        """Check if primitive is a macro"""
        return prim.name in self.macro_registry
    
    def macro_expand(self, prim: Prim) -> List[Prim]:
        """Expand macro to base primitives"""
        if not self.is_macro(prim):
            return [prim]
        
        macro_def = self.macro_registry[prim.name]
        expanded_prims = []
        
        for expanded_prim in macro_def.expansion:
            new_args = {}
            for key, value in expanded_prim.args.items():
                if isinstance(value, str) and value in macro_def.parameters:
                    param_index = macro_def.parameters.index(value)
                    if param_index < len(prim.args.get('params', [])):
                        new_args[key] = prim.args['params'][param_index]
                    else:
                        new_args[key] = value
                else:
                    new_args[key] = value
            
            expanded_prim_copy = Prim(
                name=expanded_prim.name,
                args=new_args,
                effects=expanded_prim.effects.copy(),
                budget_ms=expanded_prim.budget_ms,
                budget_calls=expanded_prim.budget_calls
            )
            expanded_prims.append(expanded_prim_copy)
        
        return expanded_prims
    
    def expand_ast(self, primitives: List[Prim]) -> List[Prim]:
        """Expand all macros in AST to base primitives"""
        expanded = []
        
        for prim in primitives:
            if self.is_macro(prim):
                macro_expanded = self.macro_expand(prim)
                expanded.extend(self.expand_ast(macro_expanded))
            else:
                expanded.append(prim)
        
        return expanded
    
    def estimate_cost(self, prim: Prim) -> float:
        """Estimate cost for a single primitive"""
        base_cost = 0.0
        
        for effect in prim.effects:
            if effect == Cap.READ:
                base_cost += self.base_costs['READ']
            elif effect == Cap.WRITE:
                base_cost += self.base_costs['WRITE']
            elif effect == Cap.NET:
                base_cost += self.base_costs['NETWORK']
            elif effect == Cap.EXEC:
                base_cost += self.base_costs['EXECUTE']
        
        compute_factor = prim.budget_ms / 1000.0  # Convert ms to seconds
        base_cost += compute_factor * self.base_costs['COMPUTE']
        
        base_cost += prim.budget_calls * 0.01
        
        return base_cost
    
    def calculate_declared_cost(self, primitives: List[Prim]) -> float:
        """Calculate declared cost without expansion"""
        total_cost = 0.0
        
        for prim in primitives:
            if self.is_macro(prim):
                total_cost += 1.0  # Flat macro cost
            else:
                total_cost += self.estimate_cost(prim)
        
        return total_cost
    
    def calculate_expanded_cost(self, primitives: List[Prim]) -> float:
        """Calculate cost after full macro expansion"""
        expanded_primitives = self.expand_ast(primitives)
        total_cost = 0.0
        
        for prim in expanded_primitives:
            total_cost += self.estimate_cost(prim)
        
        return total_cost
    
    def analyze_cost_honesty(self, execution_id: str, primitives: List[Prim]) -> CostBreakdown:
        """Analyze cost honesty for execution"""
        declared_cost = self.calculate_declared_cost(primitives)
        expanded_cost = self.calculate_expanded_cost(primitives)
        
        expanded_primitives = self.expand_ast(primitives)
        
        time_cost = sum(p.budget_ms / 1000.0 * self.base_costs['COMPUTE'] for p in expanded_primitives)
        memory_cost = sum(0.1 for p in expanded_primitives if Cap.READ in p.effects or Cap.WRITE in p.effects)
        network_cost = sum(self.base_costs['NETWORK'] for p in expanded_primitives if Cap.NET in p.effects)
        compute_cost = sum(self.base_costs['EXECUTE'] for p in expanded_primitives if Cap.EXEC in p.effects)
        
        breakdown = CostBreakdown(
            primitive_name=execution_id,
            declared_cost=declared_cost,
            expanded_cost=expanded_cost,
            time_cost=time_cost,
            memory_cost=memory_cost,
            network_cost=network_cost,
            compute_cost=compute_cost
        )
        
        if execution_id not in self.cost_history:
            self.cost_history[execution_id] = []
        self.cost_history[execution_id].append(breakdown)
        
        return breakdown
    
    def detect_macro_cheat(self, execution_id: str, threshold: float = 0.10) -> Dict[str, Any]:
        """Detect macro cost cheating (expanded cost >> declared cost)"""
        if execution_id not in self.cost_history:
            return {'error': f'No cost history for {execution_id}'}
        
        latest_breakdown = self.cost_history[execution_id][-1]
        cost_delta = latest_breakdown.cost_delta
        
        is_cheat = cost_delta > threshold
        
        return {
            'execution_id': execution_id,
            'declared_cost': latest_breakdown.declared_cost,
            'expanded_cost': latest_breakdown.expanded_cost,
            'cost_delta': cost_delta,
            'cost_delta_percent': cost_delta * 100,
            'threshold_percent': threshold * 100,
            'is_cheat': is_cheat,
            'severity': 'CRITICAL' if cost_delta > 0.5 else 'HIGH' if cost_delta > 0.25 else 'MEDIUM'
        }
    
    def generate_cost_ledger(self, execution_id: str) -> Dict[str, Any]:
        """Generate detailed cost ledger for audit"""
        if execution_id not in self.cost_history:
            return {'error': f'No cost history for {execution_id}'}
        
        breakdowns = self.cost_history[execution_id]
        
        return {
            'execution_id': execution_id,
            'total_executions': len(breakdowns),
            'cost_breakdowns': [
                {
                    'declared_cost': b.declared_cost,
                    'expanded_cost': b.expanded_cost,
                    'cost_delta': b.cost_delta,
                    'time_cost': b.time_cost,
                    'memory_cost': b.memory_cost,
                    'network_cost': b.network_cost,
                    'compute_cost': b.compute_cost
                }
                for b in breakdowns
            ],
            'average_cost_delta': sum(b.cost_delta for b in breakdowns) / len(breakdowns),
            'max_cost_delta': max(b.cost_delta for b in breakdowns),
            'cost_honesty_violations': len([b for b in breakdowns if b.cost_delta > 0.10])
        }
    
    def validate_primitive_change(self, old_prim: Optional[Prim], new_prim: Prim) -> Dict[str, Any]:
        """Validate primitive changes for cost impact"""
        if old_prim is None:
            return {
                'change_type': 'NEW',
                'requires_approval': True,
                'cost_impact': self.estimate_cost(new_prim),
                'risk_level': 'HIGH' if new_prim.effects else 'MEDIUM'
            }
        
        old_cost = self.estimate_cost(old_prim)
        new_cost = self.estimate_cost(new_prim)
        cost_change = (new_cost - old_cost) / old_cost if old_cost > 0 else float('inf')
        
        effects_changed = old_prim.effects != new_prim.effects
        
        return {
            'change_type': 'MODIFIED',
            'requires_approval': cost_change > 0.10 or effects_changed,
            'old_cost': old_cost,
            'new_cost': new_cost,
            'cost_change_percent': cost_change * 100,
            'effects_changed': effects_changed,
            'risk_level': 'CRITICAL' if effects_changed else 'HIGH' if cost_change > 0.25 else 'MEDIUM'
        }

def test_cost_honesty() -> Dict[str, Any]:
    """Test cost honesty enforcement"""
    enforcer = CostHonestyEnforcer()
    
    macro_expansion = [
        Prim(name="READ_FILE", args={}, effects={Cap.READ}, budget_ms=100, budget_calls=1),
        Prim(name="PROCESS_DATA", args={}, effects={Cap.EXEC}, budget_ms=500, budget_calls=1),
        Prim(name="WRITE_FILE", args={}, effects={Cap.WRITE}, budget_ms=100, budget_calls=1),
        Prim(name="NETWORK_CALL", args={}, effects={Cap.NET}, budget_ms=200, budget_calls=1)
    ]
    
    macro_def = MacroDefinition(
        name="COMPLEX_OPERATION",
        parameters=["input", "output"],
        expansion=macro_expansion,
        spec="Performs complex file processing with network call",
        examples=[{"input": "data.txt", "output": "result.txt"}],
        safety_proof="Bounded execution with capability restrictions",
        approvals=["reviewer1", "reviewer2"]
    )
    
    enforcer.register_macro(macro_def)
    
    test_primitives = [
        Prim(name="SIMPLE_READ", args={}, effects={Cap.READ}, budget_ms=50, budget_calls=1),
        Prim(name="COMPLEX_OPERATION", args={"params": ["input.txt", "output.txt"]}, effects={}, budget_ms=100, budget_calls=1)
    ]
    
    breakdown = enforcer.analyze_cost_honesty("test_execution", test_primitives)
    cheat_detection = enforcer.detect_macro_cheat("test_execution")
    
    return {
        'declared_cost': breakdown.declared_cost,
        'expanded_cost': breakdown.expanded_cost,
        'cost_delta': breakdown.cost_delta,
        'cost_delta_percent': breakdown.cost_delta * 100,
        'is_cheat': cheat_detection['is_cheat'],
        'cost_honesty_pass': breakdown.cost_delta <= 0.10,
        'macro_registered': True,
        'expansion_factor': len(enforcer.expand_ast(test_primitives)) / len(test_primitives)
    }
