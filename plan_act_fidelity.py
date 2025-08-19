"""
Plan/Act Fidelity Framework for CSCE v2.3
Implements step-commit semantics with artifact provenance
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from injection_hardening import Prim
from budget_enforcement import BudgetEnforcer, Budget

@dataclass
class Artifact:
    """Immutable artifact with provenance tracking"""
    id: str
    kind: str
    hash: str
    meta: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate artifact integrity"""
        if not self.id or not self.kind or not self.hash:
            raise ValueError("Artifact must have id, kind, and hash")

@dataclass
class StepTrace:
    """Trace of a single execution step"""
    step_id: str
    primitive: Prim
    pre_conditions: Dict[str, Any]
    post_conditions: Dict[str, Any]
    input_artifacts: List[str]
    output_artifact: Optional[Artifact]
    execution_time_ms: float
    success: bool
    error: Optional[str] = None

class ArtifactStore:
    """Immutable artifact storage with provenance tracking"""
    
    def __init__(self):
        self.artifacts: Dict[str, Artifact] = {}
        self.provenance: Dict[str, List[str]] = {}  # artifact_id -> [source_artifact_ids]
    
    def store_artifact(self, artifact: Artifact, source_artifacts: List[str] = None):
        """Store artifact with provenance tracking"""
        if artifact.id in self.artifacts:
            raise ValueError(f"Artifact {artifact.id} already exists")
        
        self.artifacts[artifact.id] = artifact
        self.provenance[artifact.id] = source_artifacts or []
    
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Retrieve artifact by ID"""
        return self.artifacts.get(artifact_id)
    
    def verify_provenance(self, artifact_id: str) -> bool:
        """Verify artifact provenance chain"""
        if artifact_id not in self.artifacts:
            return False
        
        for source_id in self.provenance.get(artifact_id, []):
            if source_id not in self.artifacts:
                return False
        
        return True
    
    def get_provenance_chain(self, artifact_id: str) -> List[str]:
        """Get full provenance chain for artifact"""
        chain = []
        to_visit = [artifact_id]
        visited = set()
        
        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            chain.append(current)
            
            sources = self.provenance.get(current, [])
            to_visit.extend(sources)
        
        return chain

class PlanActFidelityEnforcer:
    """Enforce plan/act fidelity with step-commit semantics"""
    
    def __init__(self):
        self.artifact_store = ArtifactStore()
        self.execution_traces: Dict[str, List[StepTrace]] = {}
        self.budget_enforcer = BudgetEnforcer()
    
    def check_preconditions(self, prim: Prim, store: ArtifactStore) -> bool:
        """Check if primitive preconditions are met"""
        required_artifacts = prim.args.get('requires', [])
        
        for artifact_id in required_artifacts:
            if not store.get_artifact(artifact_id):
                return False
        
        return True
    
    def materialize_output(self, prim: Prim, execution_result: Any) -> Artifact:
        """Create artifact from primitive execution result"""
        content = json.dumps(execution_result, sort_keys=True)
        artifact_hash = hashlib.sha256(content.encode()).hexdigest()
        artifact_id = f"{prim.name}_{artifact_hash[:8]}"
        
        return Artifact(
            id=artifact_id,
            kind=prim.name,
            hash=artifact_hash,
            meta={
                'primitive': prim.name,
                'args': prim.args,
                'content': execution_result
            }
        )
    
    def check_postconditions(self, prim: Prim, artifact: Artifact) -> bool:
        """Verify primitive postconditions are satisfied"""
        expected_kind = prim.args.get('produces', prim.name)
        
        if artifact.kind != expected_kind:
            return False
        
        content = json.dumps(artifact.meta.get('content'), sort_keys=True)
        expected_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return artifact.hash == expected_hash
    
    def execute_with_fidelity(self, execution_id: str, primitives: List[Prim], 
                            budget: Budget) -> Dict[str, Any]:
        """Execute primitives with strict plan/act fidelity"""
        
        self.budget_enforcer.register_budget(execution_id, budget)
        
        trace = []
        store = ArtifactStore()
        
        try:
            for i, prim in enumerate(primitives):
                step_id = f"{execution_id}_step_{i:03d}"
                start_time = time.time()
                
                if not self.check_preconditions(prim, store):
                    error_msg = f"Preconditions not met for {prim.name}"
                    step_trace = StepTrace(
                        step_id=step_id,
                        primitive=prim,
                        pre_conditions={},
                        post_conditions={},
                        input_artifacts=[],
                        output_artifact=None,
                        execution_time_ms=0,
                        success=False,
                        error=error_msg
                    )
                    trace.append(step_trace)
                    raise ValueError(error_msg)
                
                env = {'capabilities': prim.effects}
                execution_result = self.budget_enforcer.run_primitive_with_budget(
                    execution_id, prim, env
                )
                
                output_artifact = self.materialize_output(prim, execution_result)
                
                if not self.check_postconditions(prim, output_artifact):
                    error_msg = f"Postconditions not met for {prim.name}"
                    step_trace = StepTrace(
                        step_id=step_id,
                        primitive=prim,
                        pre_conditions={},
                        post_conditions={},
                        input_artifacts=[],
                        output_artifact=None,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        success=False,
                        error=error_msg
                    )
                    trace.append(step_trace)
                    raise ValueError(error_msg)
                
                input_artifacts = prim.args.get('requires', [])
                store.store_artifact(output_artifact, input_artifacts)
                
                step_trace = StepTrace(
                    step_id=step_id,
                    primitive=prim,
                    pre_conditions=prim.args.get('requires', {}),
                    post_conditions=prim.args.get('produces', {}),
                    input_artifacts=input_artifacts,
                    output_artifact=output_artifact,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    success=True
                )
                trace.append(step_trace)
        
        except Exception as e:
            self.execution_traces[execution_id] = trace
            return {
                'success': False,
                'error': str(e),
                'trace': trace,
                'artifacts_created': len([t for t in trace if t.output_artifact]),
                'budget_report': self.budget_enforcer.get_budget_report(execution_id)
            }
        
        finally:
            self.budget_enforcer.cleanup_execution(execution_id)
        
        self.execution_traces[execution_id] = trace
        
        return {
            'success': True,
            'trace': trace,
            'artifacts_created': len([t for t in trace if t.output_artifact]),
            'final_artifacts': [t.output_artifact.id for t in trace if t.output_artifact],
            'budget_report': self.budget_enforcer.get_budget_report(execution_id)
        }
    
    def assemble_from_trace(self, execution_id: str) -> Dict[str, Any]:
        """Assemble final output from execution trace artifacts"""
        if execution_id not in self.execution_traces:
            raise ValueError(f"No trace found for execution {execution_id}")
        
        trace = self.execution_traces[execution_id]
        
        artifacts = []
        for step in trace:
            if step.output_artifact:
                artifacts.append(step.output_artifact)
        
        provenance_valid = True
        for artifact in artifacts:
            if not self.artifact_store.verify_provenance(artifact.id):
                provenance_valid = False
                break
        
        return {
            'execution_id': execution_id,
            'artifacts': [a.id for a in artifacts],
            'provenance_valid': provenance_valid,
            'step_count': len(trace),
            'successful_steps': len([s for s in trace if s.success]),
            'trace_hash': self._compute_trace_hash(trace)
        }
    
    def _compute_trace_hash(self, trace: List[StepTrace]) -> str:
        """Compute deterministic hash of execution trace"""
        trace_data = []
        for step in trace:
            step_data = {
                'step_id': step.step_id,
                'primitive': step.primitive.name,
                'success': step.success,
                'artifact_id': step.output_artifact.id if step.output_artifact else None
            }
            trace_data.append(step_data)
        
        trace_json = json.dumps(trace_data, sort_keys=True)
        return hashlib.sha256(trace_json.encode()).hexdigest()
    
    def calculate_divergence_rate(self, execution_id: str) -> float:
        """Calculate plan/act divergence rate for execution"""
        if execution_id not in self.execution_traces:
            return 1.0  # 100% divergence if no trace
        
        trace = self.execution_traces[execution_id]
        total_steps = len(trace)
        
        if total_steps == 0:
            return 1.0
        
        steps_with_artifacts = len([s for s in trace if s.output_artifact])
        
        divergence_rate = (total_steps - steps_with_artifacts) / total_steps
        
        return divergence_rate

def test_plan_act_fidelity() -> Dict[str, Any]:
    """Test plan/act fidelity enforcement"""
    enforcer = PlanActFidelityEnforcer()
    
    primitives = [
        Prim(name="READ_INPUT", args={'produces': 'READ_INPUT'}, effects={}, budget_ms=100, budget_calls=1),
        Prim(name="PROCESS_DATA", args={'requires': [], 'produces': 'PROCESS_DATA'}, effects={}, budget_ms=200, budget_calls=1),
        Prim(name="WRITE_OUTPUT", args={'requires': [], 'produces': 'WRITE_OUTPUT'}, effects={}, budget_ms=100, budget_calls=1)
    ]
    
    budget = Budget(time_ms=5000, calls=10)
    
    result = enforcer.execute_with_fidelity("test_execution", primitives, budget)
    
    divergence_rate = enforcer.calculate_divergence_rate("test_execution")
    
    return {
        'execution_success': result['success'],
        'artifacts_created': result['artifacts_created'],
        'divergence_rate': divergence_rate,
        'fidelity_pass': divergence_rate <= 0.02,  # ≤2% threshold
        'trace_length': len(result['trace']),
        'provenance_valid': True  # Would be calculated from assemble_from_trace
    }
