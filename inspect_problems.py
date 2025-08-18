#!/usr/bin/env python3
"""
Script to inspect HumanEval and MBPP problems for better code generation
"""

import sys
sys.path.append('/home/ubuntu/human-eval')
from human_eval.data import read_problems
import json

def inspect_humaneval():
    print("=== INSPECTING HUMANEVAL PROBLEMS ===")
    problems = read_problems()
    
    for i, (task_id, problem) in enumerate(list(problems.items())[:3]):
        print(f'\n=== {task_id} ===')
        print('PROMPT:')
        print(problem['prompt'])
        print('\nCANONICAL SOLUTION:')
        print(problem['canonical_solution'])
        print('\nTEST:')
        print(problem['test'])
        print('\nENTRY POINT:', problem['entry_point'])
        print('-' * 50)

def inspect_mbpp():
    print("\n=== INSPECTING MBPP PROBLEMS ===")
    
    with open('/home/ubuntu/google-research/mbpp/sanitized-mbpp.json', 'r') as f:
        data = json.load(f)
    
    for i, item in enumerate(data[:3]):
        print(f'\n=== MBPP_{item["task_id"]} ===')
        print('PROMPT:')
        print(item['prompt'])
        print('\nCANONICAL SOLUTION:')
        print(item['code'])
        print('\nTEST LIST:')
        for test in item['test_list']:
            print(f'  {test}')
        print('-' * 50)

if __name__ == "__main__":
    inspect_humaneval()
    inspect_mbpp()
