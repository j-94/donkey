"""
Test the working CSCE v2.3 alternative with GPT-5-mini-2025-08-07
"""

import os
import time
from model_client_clean import OpenAIClient

def test_working_alternative():
    """Test the simplified CSCE alternative that should work with GPT-5-mini"""
    
    api_key = os.getenv("OPENAI_API")
    if not api_key:
        print("No API key available")
        return
    
    client = OpenAIClient(model="gpt-5-2025-08-07", temperature=0.0, api_key=api_key)
    
    working_system = """You are a structured Python code generator with metacognitive awareness.

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

Focus on correctness, clarity, and meeting the exact specifications."""
    
    def create_working_payload(entry_point: str, params: str, task_prompt: str, budget_sec: int = 30) -> str:
        return f"""TASK: Implement function {entry_point}({params})

REQUIREMENTS:
- Function must be named exactly: {entry_point}
- Parameters: {params}
- Budget: {budget_sec} seconds
- Output only Python code

PROBLEM:
{task_prompt}

CONTEXT:
Focus on correctness and exact specification compliance."""
    
    test_problems = [
        {
            "name": "Add Numbers",
            "entry_point": "add_numbers",
            "params": "a, b",
            "prompt": "Write a function that adds two numbers and returns the result."
        },
        {
            "name": "Longest Increasing Subsequence",
            "entry_point": "longest_increasing_subsequence", 
            "params": "nums",
            "prompt": "Write a function that returns the length of the longest increasing subsequence in the array using dynamic programming."
        }
    ]
    
    print("=== TESTING WORKING CSCE v2.3 ALTERNATIVE WITH GPT-5-2025-08-07 ===\n")
    
    for i, problem in enumerate(test_problems, 1):
        print(f"TEST {i}: {problem['name']}")
        print("-" * 50)
        
        payload = create_working_payload(
            problem['entry_point'], 
            problem['params'], 
            problem['prompt']
        )
        
        print("Payload preview:")
        print(payload[:200] + "..." if len(payload) > 200 else payload)
        print()
        
        try:
            start_time = time.time()
            completion = client.complete(
                system=working_system,
                user=payload,
                max_tokens=800
            )
            elapsed = time.time() - start_time
            
            print(f"✓ Generated in {elapsed:.2f}s")
            print(f"Response length: {len(completion.text)} characters")
            
            if completion.text.strip():
                print("Generated code:")
                print(completion.text)
                
                if "STATE_SIG:" in completion.text:
                    print("✓ STATE_SIG format found")
                else:
                    print("⚠ STATE_SIG format missing")
                
                if "# PLAN:" in completion.text or "# THINK:" in completion.text:
                    print("✓ Structured thinking found")
                else:
                    print("⚠ Structured thinking missing")
                    
            else:
                print("✗ Empty response")
                
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_working_alternative()
