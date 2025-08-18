"""
Diagnostic test to identify what causes GPT-5-mini-2025-08-07 to hang with CSCE v2.3
"""

import os
import time
from model_client_clean import OpenAIClient

def test_prompt_complexity():
    """Test different levels of prompt complexity to isolate the hanging issue"""
    
    api_key = os.getenv("OPENAI_API")
    if not api_key:
        print("No API key available")
        return
    
    client = OpenAIClient(model="gpt-5-mini-2025-08-07", temperature=0.0, api_key=api_key)
    
    print("=== TEST 1: Simple System Prompt ===")
    try:
        start = time.time()
        completion = client.complete(
            system="You are a Python code generator.",
            user="Write a function that adds two numbers.",
            max_tokens=200
        )
        elapsed = time.time() - start
        print(f"✓ Success in {elapsed:.2f}s - Response: {len(completion.text)} chars")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n=== TEST 2: Complex System Without Payload ===")
    complex_system = """You are a Dialogic Metaprogramming (DMP) / CSCE agent.

GOAL
- Produce correct, verifiable outputs under a bounded "seconds" budget.
- Optimize a utility tradeoff between correctness, time, and spec adherence.
- Think with explicit micro-steps; choose actions via argmax over candidates.

KEY OBJECTS (internal)
- Ψ (payload): caller-provided control block with task info, knobs, budget, tools.
- π (policy): action-selection policy parameterized by knobs in Ψ.
- A (actions): {PLAN, THINK, CRITIQUE, VERIFY, ANSWER, FINALIZE, SELF_CALL}.

OUTPUT CONTRACTS
- For code tasks: OUTPUT **only Python code** (no fences, no prose).
- Append a single-line state signature as: # STATE_SIG: {"steps":<int>,"uncertainty":<0..1>,"sec_left":<int>,"spec_ok":<bool>}"""
    
    try:
        start = time.time()
        completion = client.complete(
            system=complex_system,
            user="Write a function that adds two numbers.",
            max_tokens=200
        )
        elapsed = time.time() - start
        print(f"✓ Success in {elapsed:.2f}s - Response: {len(completion.text)} chars")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n=== TEST 3: Simple System With JSON Payload ===")
    payload_user = """<CSCE_PAYLOAD>
{
  "task_type": "code",
  "goal": "Implement function add_numbers",
  "budget_sec": 30,
  "knobs": {"u": 0, "h": "short", "r": "low", "g": 1, "a": 1}
}
</CSCE_PAYLOAD>

<PROBLEM>
Write a function that adds two numbers.
</PROBLEM>"""
    
    try:
        start = time.time()
        completion = client.complete(
            system="You are a Python code generator. Parse the payload and implement the requested function.",
            user=payload_user,
            max_tokens=200
        )
        elapsed = time.time() - start
        print(f"✓ Success in {elapsed:.2f}s - Response: {len(completion.text)} chars")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n=== TEST 4: Full CSCE System With Simple Message ===")
    from csce_generator import CSCE_SYSTEM_PROMPT
    
    try:
        start = time.time()
        completion = client.complete(
            system=CSCE_SYSTEM_PROMPT,
            user="Write a function that adds two numbers.",
            max_tokens=200
        )
        elapsed = time.time() - start
        print(f"✓ Success in {elapsed:.2f}s - Response: {len(completion.text)} chars")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n=== TEST 5: Full CSCE System With Full Payload (Expected to hang) ===")
    from csce_generator import create_csce_prompt
    
    full_payload = create_csce_prompt("add_numbers", "a, b", "Write a function that adds two numbers.", 30)
    
    print("Starting full CSCE test (may hang)...")
    try:
        start = time.time()
        completion = client.complete(
            system=CSCE_SYSTEM_PROMPT,
            user=full_payload,
            max_tokens=200
        )
        elapsed = time.time() - start
        print(f"✓ Success in {elapsed:.2f}s - Response: {len(completion.text)} chars")
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ Failed after {elapsed:.2f}s: {e}")

if __name__ == "__main__":
    test_prompt_complexity()
