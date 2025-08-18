#!/usr/bin/env python3
"""
Debug script to see what code is being generated and why tests are failing
"""

import sys
sys.path.append('/home/ubuntu/human-eval')
from human_eval.data import read_problems
from real_world_csce_tester import CSCECodeGenerator, RealWorldCodeExecutor
import json

def debug_humaneval():
    print("=== DEBUGGING HUMANEVAL CODE GENERATION ===")
    
    problems = read_problems()
    generator = CSCECodeGenerator()
    executor = RealWorldCodeExecutor()
    
    for i, (task_id, problem) in enumerate(list(problems.items())[:3]):
        print(f'\n=== {task_id} ===')
        print('PROMPT:')
        print(problem['prompt'][:200] + "...")
        
        generated_code, steps, uncertainty = generator.generate_solution(problem['prompt'], time_limit=10)
        
        print('\nGENERATED CODE:')
        print(generated_code)
        
        full_code = generated_code + "\n" + problem['test']
        success, stdout, stderr = executor.execute_code(full_code)
        
        print(f'\nEXECUTION SUCCESS: {success}')
        if stdout:
            print(f'STDOUT: {stdout}')
        if stderr:
            print(f'STDERR: {stderr}')
        
        print('-' * 60)

def debug_mbpp():
    print("\n=== DEBUGGING MBPP CODE GENERATION ===")
    
    with open('/home/ubuntu/google-research/mbpp/sanitized-mbpp.json', 'r') as f:
        data = json.load(f)
    
    generator = CSCECodeGenerator()
    executor = RealWorldCodeExecutor()
    
    for i, item in enumerate(data[:3]):
        print(f'\n=== MBPP_{item["task_id"]} ===')
        print('PROMPT:')
        print(item['prompt'])
        
        generated_code, steps, uncertainty = generator.generate_solution(item['prompt'], time_limit=10)
        
        print('\nGENERATED CODE:')
        print(generated_code)
        
        test_code = "\n".join(item['test_list'])
        full_code = item.get('test_setup_code', '') + "\n" + generated_code + "\n" + test_code
        
        print('\nFULL CODE TO EXECUTE:')
        print(full_code)
        
        success, stdout, stderr = executor.execute_code(full_code)
        
        print(f'\nEXECUTION SUCCESS: {success}')
        if stdout:
            print(f'STDOUT: {stdout}')
        if stderr:
            print(f'STDERR: {stderr}')
        
        print('-' * 60)

if __name__ == "__main__":
    debug_humaneval()
    debug_mbpp()
