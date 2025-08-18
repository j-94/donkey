"""
Vanilla code generator using direct model calls without CSCE policy
"""

from model_client_clean import ModelClient, Completion

class VanillaGenerator:
    """Vanilla code generator that makes direct model calls"""
    
    def __init__(self, client: ModelClient, system_prompt: str):
        self.client = client
        self.system_prompt = system_prompt
    
    def generate(self, prompt: str, seconds_budget: int, entry_point: str = None, arity: int = None) -> tuple[str, float]:
        """Generate code using vanilla approach (single model call)"""
        if entry_point and arity is not None:
            params = ",".join([f"a{i}" for i in range(arity)])
            user_prompt = create_vanilla_prompt(entry_point, params, prompt)
            system_prompt = "You are a Python code generator."
        else:
            user_prompt = prompt
            system_prompt = self.system_prompt
            
        completion: Completion = self.client.complete(
            system=system_prompt,
            user=user_prompt,
            temperature=0.0
        )
        
        code = self._strip_markdown(completion.text)
        return code, completion.latency_s
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown code block formatting"""
        import re
        text = re.sub(r'^```python\s*\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text)
        text = text.strip('`').strip()
        return text

def create_vanilla_prompt(entry_point: str, params: str, task_prompt: str) -> str:
    """Create name-strict vanilla prompt"""
    return f"""You are a Python solver.

HARD RULES:
- Implement exactly one top-level function named: {entry_point}
- Use this signature shape (names don't matter): def {entry_point}({params}): ...
- No other top-level functions or prints.
- Output a single valid Python file, no markdown fences/backticks, no prose.

Task:
{task_prompt}

Return only the .py file content."""

VANILLA_SYSTEM_PROMPT = """You are a Python code generator. Given a problem statement, output a single Python file that:
- Defines the required entry point (if provided).
- Contains only code (no markdown/prose).
- Uses standard library only unless otherwise stated.
Avoid extra comments."""
