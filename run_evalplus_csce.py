"""
EvalPlus integration for CSCE vs vanilla evaluation with proper contract matching
"""

import json
import time
import re
from typing import Dict, Any, List
from evalplus.sanitize import get_human_eval_plus, get_mbpp_plus

from model_client_clean import OpenAIClient
from vanilla_generator import VanillaGenerator, VANILLA_SYSTEM_PROMPT
from csce_generator import CSCEPolicyGenerator, CSCE_SYSTEM_PROMPT, create_csce_prompt
from csce_kernel import PayloadKnobs

def coerce_function_name(solution_code: str, expected_entry_point: str) -> str:
    """
    Coerce the function name in solution code to match the expected entry point.
    This fixes contract mismatches where models generate different function names.
    """
    import ast
    import re
    
    try:
        tree = ast.parse(solution_code)
        
        function_defs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if not function_defs:
            return solution_code
        
        main_func = max(function_defs, key=lambda f: f.end_lineno - f.lineno)
        current_name = main_func.name
        
        if current_name == expected_entry_point:
            return solution_code
        
        pattern = rf'\bdef\s+{re.escape(current_name)}\s*\('
        replacement = f'def {expected_entry_point}('
        
        coerced_code = re.sub(pattern, replacement, solution_code)
        
        func_call_pattern = rf'\b{re.escape(current_name)}\s*\('
        func_call_replacement = f'{expected_entry_point}('
        coerced_code = re.sub(func_call_pattern, func_call_replacement, coerced_code)
        
        return coerced_code
        
    except Exception as e:
        print(f"Warning: AST parsing failed for coercion, using regex fallback: {e}")
        def_pattern = r'def\s+(\w+)\s*\('
        match = re.search(def_pattern, solution_code)
        if match:
            current_name = match.group(1)
            if current_name != expected_entry_point:
                pattern = rf'\bdef\s+{re.escape(current_name)}\s*\('
                replacement = f'def {expected_entry_point}('
                solution_code = re.sub(pattern, replacement, solution_code)
                
                func_call_pattern = rf'\b{re.escape(current_name)}\s*\('
                func_call_replacement = f'{expected_entry_point}('
                solution_code = re.sub(func_call_pattern, func_call_replacement, solution_code)
        
        return solution_code

def call_model_with(policy: str, prompt: str, entry_point: str = None) -> str:
    """
    Call model with specified policy (vanilla or csce)
    Returns the generated solution code
    """
    import os
    api_key = os.getenv("OPENAI_API") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Set OPENAI_API or OPENAI_API_KEY environment variable.")
    
    client = OpenAIClient(model="gpt-5-mini", temperature=0.2, api_key=api_key)
    
    if policy == "vanilla":
        generator = VanillaGenerator(client, VANILLA_SYSTEM_PROMPT)
        if entry_point:
            arity = _infer_arity_from_prompt(prompt, entry_point)
            code, latency = generator.generate(prompt, seconds_budget=30, entry_point=entry_point, arity=arity)
        else:
            code, latency = generator.generate(prompt, seconds_budget=30)
        
    elif policy == "csce":
        if entry_point:
            arity = _infer_arity_from_prompt(prompt, entry_point)
            params = ",".join([f"a{i}" for i in range(arity)])
            user_prompt = create_csce_prompt(entry_point, params, prompt, budget_sec=30)
        else:
            user_prompt = prompt
            
        completion = client.complete(
            system=CSCE_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.2
        )
        code = completion.text
        
        code = _strip_markdown_enhanced(code)
    
    else:
        raise ValueError(f"Unknown policy: {policy}")
    
    return code

def _strip_markdown_enhanced(text: str) -> str:
    """Enhanced markdown stripping for v2.3 responses that may include explanatory text"""
    import re
    
    text = re.sub(r'^```python\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'```$', '', text)
    text = text.strip('`').strip()
    
    lines = text.split('\n')
    code_start = -1
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.startswith('def ') or 
            stripped.startswith('import ') or 
            stripped.startswith('from ') or
            stripped.startswith('class ') or
            (stripped and not stripped.startswith('#') and '=' in stripped)):
            code_start = i
            break
    
    if code_start >= 0:
        text = '\n'.join(lines[code_start:])
    
    if '# STATE_SIG:' in text:
        sig_index = text.rfind('# STATE_SIG:')
        sig_line_end = text.find('\n', sig_index)
        if sig_line_end == -1:
            sig_line_end = len(text)
        else:
            sig_line_end += 1
        text = text[:sig_line_end]
    
    return text.strip()

def _infer_arity_from_prompt(prompt: str, entry_point: str) -> int:
    """Infer function arity from prompt text"""
    patterns = [
        rf'def\s+{re.escape(entry_point)}\s*\(([^)]*)\)',
        rf'{re.escape(entry_point)}\s*\(([^)]*)\)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            params_str = match.group(1).strip()
            if not params_str:
                return 0
            params = [p.strip() for p in params_str.split(',') if p.strip()]
            return len(params)
    
    return 2

def dump_jsonl(rows: List[Dict], path: str):
    """Write predictions to JSONL format"""
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def run_split(dataset: Dict, out_path: str, policy: str):
    """Generate solutions for a dataset split using specified policy"""
    rows = []
    total_problems = len(dataset)
    
    print(f"Generating {policy} solutions for {total_problems} problems...")
    
    for i, (task_id, task_data) in enumerate(dataset.items()):
        print(f"  {i+1}/{total_problems}: {task_id}")
        
        try:
            solution = call_model_with(policy, task_data["prompt"], task_data.get("entry_point"))
            
            if "entry_point" in task_data:
                solution = coerce_function_name(solution, task_data["entry_point"])
            
            rows.append({
                "task_id": task_id,
                "solution": solution
            })
            
        except Exception as e:
            print(f"    Error generating solution: {e}")
            rows.append({
                "task_id": task_id,
                "solution": f"# Error: {str(e)}\ndef placeholder(): pass"
            })
    
    dump_jsonl(rows, out_path)
    print(f"Saved {len(rows)} predictions to {out_path}")

def main():
    """Main function to run EvalPlus CSCE evaluation"""
    print("=== EVALPLUS CSCE EVALUATION ===")
    print("Loading datasets...")
    
    humaneval_plus = get_human_eval_plus()
    mbpp_plus = get_mbpp_plus()
    
    print(f"Loaded {len(humaneval_plus)} HumanEval+ problems")
    print(f"Loaded {len(mbpp_plus)} MBPP+ problems")
    
    he_subset = dict(list(humaneval_plus.items())[:50])  # First 50 HumanEval+ problems for faster evaluation
    mb_subset = dict(list(mbpp_plus.items())[:25])  # First 25 MBPP+ problems for faster evaluation
    
    print(f"\nRunning on: {len(he_subset)} HumanEval+ + {len(mb_subset)} MBPP+")
    
    print("\n=== HUMANEVAL+ ===")
    run_split(he_subset, "he_vanilla.jsonl", "vanilla")
    run_split(he_subset, "he_csce.jsonl", "csce")
    
    print("\n=== MBPP+ ===")
    run_split(mb_subset, "mb_vanilla.jsonl", "vanilla")
    run_split(mb_subset, "mb_csce.jsonl", "csce")
    
    print("\n=== EVALUATION COMPLETE ===")
    print("Generated prediction files:")
    print("  - he_vanilla.jsonl (HumanEval+ vanilla)")
    print("  - he_csce.jsonl (HumanEval+ CSCE)")
    print("  - mb_vanilla.jsonl (MBPP+ vanilla)")
    print("  - mb_csce.jsonl (MBPP+ CSCE)")
    
    print("\nTo evaluate, run:")
    print("  python -m evalplus.evaluate --dataset humaneval --samples he_vanilla.jsonl")
    print("  python -m evalplus.evaluate --dataset humaneval --samples he_csce.jsonl")
    print("  python -m evalplus.evaluate --dataset mbpp --samples mb_vanilla.jsonl")
    print("  python -m evalplus.evaluate --dataset mbpp --samples mb_csce.jsonl")

if __name__ == "__main__":
    main()
