"""
Comprehensive test suite for CSCE v2.3 Dialogic Metaprogramming system
Tests complex problems that benefit from structured PLAN/THINK/CRITIQUE approach
"""

import os
import time
import argparse
from model_client_clean import OpenAIClient
from simple_mock_client import SimpleMockClient
from csce_generator import create_csce_prompt, CSCE_SYSTEM_PROMPT
from vanilla_generator import VANILLA_SYSTEM_PROMPT
from run_evalplus_csce import _strip_markdown_enhanced

def test_complex_algorithm_design():
    """Test complex algorithm that requires planning and multi-step reasoning"""
    
    problem = """
Design and implement a function that finds the longest increasing subsequence (LIS) in an array.
The function should:
1. Take an array of integers as input
2. Return the length of the longest increasing subsequence
3. Use dynamic programming for optimal O(n²) solution
4. Handle edge cases (empty array, single element, all decreasing)

Example: [10, 9, 2, 5, 3, 7, 101, 18] should return 4 (subsequence: [2, 3, 7, 101])

Requirements:
- Function name: longest_increasing_subsequence
- Parameter: nums (list of integers)
- Return: integer (length of LIS)
- Must use dynamic programming approach
"""
    
    return {
        "name": "Longest Increasing Subsequence",
        "problem": problem,
        "entry_point": "longest_increasing_subsequence",
        "test_cases": [
            ([10, 9, 2, 5, 3, 7, 101, 18], 4),
            ([0, 1, 0, 3, 2, 3], 4),
            ([7, 7, 7, 7, 7, 7, 7], 1),
            ([], 0),
            ([1], 1),
            ([5, 4, 3, 2, 1], 1),
            ([1, 2, 3, 4, 5], 5)
        ]
    }

def test_complex_data_structure():
    """Test implementation of complex data structure requiring careful design"""
    
    problem = """
Implement a LRU (Least Recently Used) Cache with the following operations:
1. get(key): Get the value of the key if it exists, otherwise return -1
2. put(key, value): Set or insert the value if the key is not already present
3. When the cache reaches its capacity, invalidate the least recently used item

The cache should support O(1) time complexity for both get and put operations.

Requirements:
- Class name: LRUCache
- Constructor: __init__(self, capacity: int)
- Methods: get(self, key: int) -> int, put(self, key: int, value: int) -> None
- Must maintain O(1) time complexity for both operations
- Use doubly linked list + hash map for optimal implementation

Example usage:
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
cache.get(1)    # returns 1
cache.put(3, 3) # evicts key 2
cache.get(2)    # returns -1 (not found)
"""
    
    return {
        "name": "LRU Cache Implementation",
        "problem": problem,
        "entry_point": "LRUCache",
        "test_cases": [
        ]
    }

def test_complex_graph_algorithm():
    """Test graph algorithm requiring systematic approach"""
    
    problem = """
Implement Dijkstra's shortest path algorithm to find the shortest path from a source vertex 
to all other vertices in a weighted graph.

The function should:
1. Take a graph represented as adjacency list with weights
2. Take a source vertex
3. Return a dictionary with shortest distances to all vertices
4. Handle disconnected vertices (return infinity or -1)
5. Use a priority queue for optimal performance

Graph format: {vertex: [(neighbor, weight), ...]}
Example: {0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 5)], 3: []}

Requirements:
- Function name: dijkstra_shortest_path
- Parameters: graph (dict), source (int)
- Return: dict mapping vertex -> shortest distance
- Must use priority queue (heapq)
- Handle edge cases (empty graph, unreachable vertices)
"""
    
    return {
        "name": "Dijkstra's Shortest Path",
        "problem": problem,
        "entry_point": "dijkstra_shortest_path",
        "test_cases": [
            ({0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 5)], 3: []}, 0, {0: 0, 1: 3, 2: 1, 3: 4}),
            ({0: [(1, 1)], 1: [(2, 1)], 2: []}, 0, {0: 0, 1: 1, 2: 2}),
            ({}, 0, {}),
            ({0: [], 1: []}, 0, {0: 0, 1: float('inf')})
        ]
    }

def test_complex_string_processing():
    """Test complex string processing requiring careful parsing"""
    
    problem = """
Implement a function that evaluates a mathematical expression given as a string.
The expression can contain:
- Integers (positive and negative)
- Basic operators: +, -, *, /
- Parentheses for grouping
- Spaces (should be ignored)

The function should:
1. Parse the expression correctly respecting operator precedence
2. Handle parentheses properly
3. Return the result as a float
4. Handle division by zero gracefully (return None or raise exception)

Examples:
- "2 + 3 * 4" should return 14.0
- "(2 + 3) * 4" should return 20.0
- "10 / 2 - 3" should return 2.0
- "2 * (3 + 4) / 2" should return 7.0

Requirements:
- Function name: evaluate_expression
- Parameter: expression (string)
- Return: float (result) or None (if invalid/division by zero)
- Must handle operator precedence correctly
- Must handle parentheses correctly
"""
    
    return {
        "name": "Mathematical Expression Evaluator",
        "problem": problem,
        "entry_point": "evaluate_expression",
        "test_cases": [
            ("2 + 3 * 4", 14.0),
            ("(2 + 3) * 4", 20.0),
            ("10 / 2 - 3", 2.0),
            ("2 * (3 + 4) / 2", 7.0),
            ("1 + 2 * 3 - 4 / 2", 5.0),
            ("((1 + 2) * 3 - 4) / 2", 2.5)
        ]
    }

def test_complex_optimization_problem():
    """Test optimization problem requiring strategic thinking"""
    
    problem = """
Implement the 0/1 Knapsack problem using dynamic programming.
Given a set of items, each with a weight and value, determine the maximum value 
that can be obtained with a weight limit.

The function should:
1. Take a list of items (weight, value) and a capacity limit
2. Return the maximum value achievable within the weight limit
3. Use dynamic programming for optimal solution
4. Handle edge cases (no items, zero capacity, items too heavy)

Example:
Items: [(2, 1), (3, 4), (4, 5), (5, 7)]
Capacity: 8
Result: 9 (items with weights 3 and 5, values 4 and 5)

Requirements:
- Function name: knapsack_01
- Parameters: items (list of tuples), capacity (int)
- Return: int (maximum value)
- Must use dynamic programming approach
- Time complexity: O(n * capacity)
"""
    
    return {
        "name": "0/1 Knapsack Problem",
        "problem": problem,
        "entry_point": "knapsack_01",
        "test_cases": [
            ([(2, 1), (3, 4), (4, 5), (5, 7)], 8, 9),
            ([(1, 1), (2, 4), (3, 7)], 5, 11),
            ([], 10, 0),
            ([(5, 10)], 3, 0),
            ([(1, 1)], 1, 1)
        ]
    }

def run_comprehensive_evaluation(use_mock=False):
    """Run comprehensive evaluation on complex problems"""
    
    print("=== COMPREHENSIVE CSCE v2.3 TEST SUITE ===")
    print("Testing complex problems that benefit from structured thinking\n")
    
    test_problems = [
        test_complex_algorithm_design(),
        test_complex_data_structure(),
        test_complex_graph_algorithm(),
        test_complex_string_processing(),
        test_complex_optimization_problem()
    ]
    
    if use_mock:
        client = SimpleMockClient(mock_latency=0.5)
        print("Using SimpleMockClient for testing system structure")
    else:
        api_key = os.getenv("OPENAI_API") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("No API key found, falling back to mock client")
            client = SimpleMockClient(mock_latency=0.5)
            use_mock = True
        else:
            client = OpenAIClient(model="gpt-5-2025-08-07", temperature=0.2, api_key=api_key)
            print("Using GPT-5-2025-08-07 for real evaluation")
    
    results = {
        "vanilla": [],
        "csce_v23": []
    }
    
    for problem in test_problems:
        print(f"\n{'='*60}")
        print(f"TESTING: {problem['name']}")
        print(f"{'='*60}")
        
        print(f"\n--- VANILLA APPROACH ---")
        try:
            vanilla_start = time.time()
            vanilla_completion = client.complete(
                system=VANILLA_SYSTEM_PROMPT,
                user=problem["problem"],
                temperature=0.2
            )
            vanilla_time = time.time() - vanilla_start
            
            vanilla_code = _strip_markdown_enhanced(vanilla_completion.text)
            print(f"Generated in {vanilla_time:.2f}s")
            print("Code preview:")
            print('\n'.join(vanilla_code.split('\n')[:10]))
            if len(vanilla_code.split('\n')) > 10:
                print("... (truncated)")
            
            results["vanilla"].append({
                "problem": problem["name"],
                "code": vanilla_code,
                "time": vanilla_time,
                "success": True
            })
            
        except Exception as e:
            print(f"Vanilla failed: {e}")
            results["vanilla"].append({
                "problem": problem["name"],
                "code": f"# Error: {e}",
                "time": 0,
                "success": False
            })
        
        print(f"\n--- CSCE v2.3 APPROACH ---")
        try:
            csce_start = time.time()
            
            if problem["entry_point"] == "LRUCache":
                params = "capacity"
            else:
                if "nums" in problem["problem"]:
                    params = "nums"
                elif "graph" in problem["problem"] and "source" in problem["problem"]:
                    params = "graph, source"
                elif "expression" in problem["problem"]:
                    params = "expression"
                elif "items" in problem["problem"] and "capacity" in problem["problem"]:
                    params = "items, capacity"
                else:
                    params = "args"
            
            csce_prompt = create_csce_prompt(
                problem["entry_point"], 
                params, 
                problem["problem"], 
                budget_sec=60
            )
            
            csce_completion = client.complete(
                system=CSCE_SYSTEM_PROMPT,
                user=csce_prompt,
                temperature=0.2
            )
            csce_time = time.time() - csce_start
            
            csce_code = _strip_markdown_enhanced(csce_completion.text)
            print(f"Generated in {csce_time:.2f}s")
            print("Code preview:")
            print('\n'.join(csce_code.split('\n')[:10]))
            if len(csce_code.split('\n')) > 10:
                print("... (truncated)")
            
            if "# STATE_SIG:" in csce_code:
                print("✓ STATE_SIG found in response")
            else:
                print("⚠ STATE_SIG missing from response")
            
            results["csce_v23"].append({
                "problem": problem["name"],
                "code": csce_code,
                "time": csce_time,
                "success": True
            })
            
        except Exception as e:
            print(f"CSCE v2.3 failed: {e}")
            results["csce_v23"].append({
                "problem": problem["name"],
                "code": f"# Error: {e}",
                "time": 0,
                "success": False
            })
    
    print(f"\n{'='*60}")
    print("COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    vanilla_success = sum(1 for r in results["vanilla"] if r["success"])
    csce_success = sum(1 for r in results["csce_v23"] if r["success"])
    total_problems = len(test_problems)
    
    vanilla_avg_time = sum(r["time"] for r in results["vanilla"] if r["success"]) / max(vanilla_success, 1)
    csce_avg_time = sum(r["time"] for r in results["csce_v23"] if r["success"]) / max(csce_success, 1)
    
    print(f"Vanilla Success Rate: {vanilla_success}/{total_problems} ({vanilla_success/total_problems*100:.1f}%)")
    print(f"CSCE v2.3 Success Rate: {csce_success}/{total_problems} ({csce_success/total_problems*100:.1f}%)")
    print(f"Vanilla Avg Time: {vanilla_avg_time:.2f}s")
    print(f"CSCE v2.3 Avg Time: {csce_avg_time:.2f}s")
    
    import json
    with open("comprehensive_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to comprehensive_test_results.json")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CSCE v2.3 comprehensive test suite")
    parser.add_argument("--mock", action="store_true", help="Use mock client instead of real API")
    args = parser.parse_args()
    
    run_comprehensive_evaluation(use_mock=args.mock)
