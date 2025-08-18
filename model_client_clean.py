"""
Clean model client interface for real LLM inference calls
"""

from dataclasses import dataclass
from typing import Optional
import time
import os

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class Completion:
    text: str
    latency_s: float

class ModelClient:
    """Abstract base class for model clients"""
    
    def complete(self, system: str, user: str, temperature: float = 0.0, max_tokens: int = 512) -> Completion:
        raise NotImplementedError

class OpenAIClient(ModelClient):
    """OpenAI API client for real model inference"""
    
    def __init__(self, model: str = "gpt-5-2025-08-07", api_key: Optional[str] = None, temperature: float = 0.0):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        
        self.model = model
        self.default_temperature = temperature
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def complete(self, system: str, user: str, temperature: float = None, max_tokens: int = 512) -> Completion:
        start_time = time.time()
        
        if temperature is None:
            temperature = self.default_temperature
        
        try:
            # GPT-5 has specific parameter requirements
            if "gpt-5" in self.model:
                # GPT-5 uses max_completion_tokens and only supports default temperature (1)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    max_completion_tokens=8192  # Maximum tokens for GPT-5 reasoning
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    temperature=temperature,
                    max_tokens=8192  # Maximum tokens for GPT-5
                )
            
            latency = time.time() - start_time
            
            import json
            print(f"[DEBUG] Model: {self.model}")
            print(f"[DEBUG] Response dump: {json.dumps(response.model_dump(), indent=2)[:2000]}")
            
            msg = response.choices[0].message
            
            if msg.content:
                text = msg.content
                print(f"[DEBUG] Got content: {len(text)} chars")
            elif msg.tool_calls:
                tool_info = []
                for tc in msg.tool_calls:
                    tool_info.append(f"{tc.function.name}({tc.function.arguments})")
                    print(f"[TOOL_CALL] {tc.function.name}({tc.function.arguments})")
                text = f"# Model attempted tool calls: {', '.join(tool_info)}\n# Please implement tool loop or use tool_choice='none'"
                print(f"[DEBUG] Got tool_calls instead of content")
            else:
                text = "# No content or tool_calls returned"
                print(f"[DEBUG] No content or tool_calls found")
            
            return Completion(text=text, latency_s=latency)
            
        except Exception as e:
            latency = time.time() - start_time
            print(f"API Error: {str(e)}")  # Debug output
            return Completion(text=f"# Error: {str(e)}", latency_s=latency)

class MockClient(ModelClient):
    """Mock client for testing without API calls"""
    
    def __init__(self, mock_latency: float = 0.5):
        self.mock_latency = mock_latency
    
    def complete(self, system: str, user: str, temperature: float = 0.0, max_tokens: int = 512) -> Completion:
        time.sleep(self.mock_latency)  # Simulate network latency
        
        imports = ""
        if "List[" in user:
            imports = "from typing import List\n"
        
        if "def " in user:
            lines = user.split('\n')
            for line in lines:
                if line.strip().startswith('def '):
                    func_signature = line.strip()
                    func_name = func_signature.split('(')[0].replace('def ', '')
                    
                    if 'has_close_elements' in func_name:
                        code = f"{imports}{func_signature}\n    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n    return False"
                    
                    elif 'separate_paren_groups' in func_name:
                        code = f"{imports}{func_signature}\n    result = []\n    current_string = []\n    current_depth = 0\n    \n    for c in paren_string:\n        if c == '(':\n            current_depth += 1\n            current_string.append(c)\n        elif c == ')':\n            current_depth -= 1\n            current_string.append(c)\n            \n            if current_depth == 0:\n                result.append(''.join(current_string))\n                current_string.clear()\n    \n    return result"
                    
                    elif 'truncate_number' in func_name:
                        code = f"{imports}{func_signature}\n    return number % 1.0"
                    
                    else:
                        code = f"{imports}{func_signature}\n    pass  # Mock implementation"
                    
                    return Completion(text=code, latency_s=self.mock_latency)
        
        elif 'shared elements' in user.lower():
            code = "def similar_elements(test_tup1, test_tup2):\n    res = tuple(set(test_tup1) & set(test_tup2))\n    return res"
            return Completion(text=code, latency_s=self.mock_latency)
        
        elif 'non-prime' in user.lower() or 'not prime' in user.lower():
            code = "import math\ndef is_not_prime(n):\n    if n <= 1:\n        return True\n    if n == 2:\n        return False\n    result = False\n    for i in range(2, int(math.sqrt(n)) + 1):\n        if n % i == 0:\n            result = True\n            break\n    return result"
            return Completion(text=code, latency_s=self.mock_latency)
        
        return Completion(
            text="# Mock response - implement the requested function",
            latency_s=self.mock_latency
        )
