"""
CSCE policy-driven code generator using the CSCE v2.3 Dialogic Metaprogramming system
"""

import json
from model_client_clean import ModelClient, Completion
from csce_kernel import CSCEKernel, ActionType, PayloadKnobs

class CSCEPolicyGenerator:
    """CSCE policy-driven generator that uses the kernel to guide model calls"""
    
    def __init__(self, client: ModelClient, policy_sys_prompt: str, knobs: PayloadKnobs):
        self.client = client
        self.policy_sys_prompt = policy_sys_prompt
        self.knobs = knobs
    
    def generate(self, prompt: str, seconds_budget: int, entry_point: str = None, arity: int = None) -> tuple[str, int, float, float]:
        """
        Generate code using CSCE policy
        Returns: (code, steps, final_uncertainty, total_latency)
        """
        kernel = CSCEKernel(initial_budget_sec=seconds_budget)
        kernel.knobs = self.knobs
        
        steps = 0
        code = ""
        total_latency = 0.0
        
        if entry_point and arity is not None:
            params = ",".join([f"a{i}" for i in range(arity)])
            user_prompt = create_csce_prompt(entry_point, params, prompt)
            system_prompt = "You are a Python code generator with CSCE policy."
        else:
            user_prompt = prompt
            system_prompt = self.policy_sys_prompt
        
        while kernel.state.resources_sec_left > 2 and steps < 15:
            action_candidate = kernel.select_action(user_prompt)
            steps += 1
            
            if action_candidate.action == ActionType.ANSWER:
                completion = self.client.complete(
                    system=system_prompt,
                    user=user_prompt,
                    temperature=0.0
                )
                code = self._strip_markdown(completion.text)
                total_latency += completion.latency_s
                
                kernel.state.resources_sec_left -= completion.latency_s
                break
            
            kernel.execute_action(action_candidate, user_prompt)
        
        if not code:
            completion = self.client.complete(
                system=system_prompt,
                user=user_prompt,
                temperature=0.0
            )
            code = completion.text
            total_latency += completion.latency_s
        
        code = self._strip_markdown(code)
        return code, steps, kernel.state.uncertainty, total_latency
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown code block formatting"""
        import re
        # Remove ```python and ``` blocks
        text = re.sub(r'^```python\s*\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text)
        text = text.strip('`').strip()
        return text

def create_csce_prompt(entry_point: str, params: str, task_prompt: str, budget_sec: int = 30) -> str:
    """Create CSCE v2.3 prompt with full payload schema"""
    payload = {
        "task_type": "code",
        "goal": f"Implement function {entry_point} that solves the given problem",
        "dod": [
            f"Function named exactly '{entry_point}' is defined",
            f"Function signature matches: def {entry_point}({params}): ...",
            "Code compiles without errors",
            "Function implements the required logic correctly",
            "No extra top-level functions or print statements"
        ],
        "constraints": [
            f"Must define exactly: def {entry_point}({params}): ...",
            "Output only Python code, no markdown fences",
            "Use standard library only unless specified"
        ],
        "budget_sec": budget_sec,
        "knobs": {"u": 0, "h": "short", "r": "low", "g": 1, "a": 1},
        "lambdas": {"time": 0.1, "risk": 0.2},
        "conf_thresh": 0.8,
        "self_call": {"q_seconds": 2, "max_repeats": 2},
        "answer_format": "code",
        "code_contract": {
            "entry_point": entry_point,
            "imports_allowed": ["*"],
            "tests": {"type": "inline", "inline": ""}
        },
        "tools": [
            {"name": "run_tests", "enabled": False},
            {"name": "run_code", "enabled": False}
        ],
        "gates": {
            "ENABLE_VERIFY": True,
            "ENABLE_TOOLS": False,
            "STRICT_ENTRY_POINT": True
        }
    }
    
    return f"""<CSCE_PAYLOAD>
{json.dumps(payload, indent=2)}
</CSCE_PAYLOAD>

<PROBLEM>
{task_prompt}
</PROBLEM>

<CONTEXT>
You must implement the function with the exact name and signature specified in the payload.
Focus on correctness and spec adherence.
</CONTEXT>"""

CSCE_SYSTEM_PROMPT = """You are a structured Python code generator with metacognitive awareness.

You do NOT have tools in this run. Never emit tool_calls. Always respond with plain text only.
If you would normally call a tool, briefly say what you would have done and then answer directly.

APPROACH:
1. PLAN: Analyze the problem and break it into steps
2. THINK: Consider implementation approach and edge cases
3. IMPLEMENT: Write clean, correct Python code
4. VERIFY: Check solution against requirements

CONSTRAINTS:
- Output only Python code (no markdown fences)
- Include brief planning comments at the top
- Define the exact function signature requested
- Handle edge cases appropriately

OUTPUT FORMAT:
- Planning comments (# PLAN: ...)
- Implementation code
- Final line: # STATE_SIG: {"steps":<int>,"uncertainty":<0..1>,"sec_left":<int>,"spec_ok":<bool>}

Focus on correctness, clarity, and meeting the exact specifications.
Always end with a line that begins with: # STATE_SIG:"""
