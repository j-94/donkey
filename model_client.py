"""
Model client interface for real LLM inference calls
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
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, temperature: float = 0.0):
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            latency = time.time() - start_time
            text = response.choices[0].message.content or ""
            
            return Completion(text=text, latency_s=latency)
            
        except Exception as e:
            latency = time.time() - start_time
            return Completion(text=f"# Error: {str(e)}", latency_s=latency)

class MockClient(ModelClient):
    """Mock client for testing without API calls"""
    
    def __init__(self, mock_latency: float = 0.5):
        self.mock_latency = mock_latency
    
    def complete(self, system: str, user: str, temperature: float = 0.0, max_tokens: int = 512) -> Completion:
        time.sleep(self.mock_latency)  # Simulate network latency
        
        if "CSCE_PAYLOAD" in user and "Dialogic Metaprogramming" in system:
            if "longest_increasing_subsequence" in user.lower():
                code = """# PLAN
1. Understand the problem: find longest increasing subsequence length
2. Use dynamic programming approach with O(n²) complexity
3. Handle edge cases: empty array, single element

For each position i, dp[i] represents the length of LIS ending at position i.
For each i, check all previous positions j where arr[j] < arr[i].

def longest_increasing_subsequence(nums):
    if not nums:
        return 0
    
    n = len(nums)
    dp = [1] * n
    
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    
    return max(dp)

                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "lrucache" in user.lower():
                code = """# PLAN
1. Design LRU Cache with O(1) get/put operations
2. Use doubly linked list + hash map combination
3. Implement capacity management and eviction policy

Need to maintain order of access while allowing O(1) lookups.
Hash map for O(1) access, doubly linked list for O(1) insertion/deletion.

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = self.Node(0, 0)
        self.tail = self.Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    class Node:
        def __init__(self, key, val):
            self.key = key
            self.val = val
            self.prev = None
            self.next = None
    
    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add(node)
            return node.val
        return -1
    
    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])
        node = self.Node(key, value)
        self._add(node)
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            lru = self.head.next
            self._remove(lru)
            del self.cache[lru.key]
    
    def _add(self, node):
        prev_node = self.tail.prev
        prev_node.next = node
        node.prev = prev_node
        node.next = self.tail
        self.tail.prev = node
    
    def _remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "dijkstra" in user.lower():
                code = """# PLAN
1. Implement Dijkstra's algorithm using priority queue
2. Handle graph as adjacency list with weights
3. Return shortest distances to all vertices from source

Use heapq for priority queue. Initialize distances to infinity except source.
Process vertices in order of shortest distance, updating neighbors.

import heapq

def dijkstra_shortest_path(graph, source):
    if not graph:
        return {}
    
    distances = {vertex: float('inf') for vertex in graph}
    distances[source] = 0
    pq = [(0, source)]
    
    while pq:
        current_dist, current_vertex = heapq.heappop(pq)
        
        if current_dist > distances[current_vertex]:
            continue
        
        for neighbor, weight in graph.get(current_vertex, []):
            distance = current_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances

                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "evaluate_expression" in user.lower():
                code = """# PLAN
1. Parse mathematical expression with operator precedence
2. Handle parentheses using recursive descent or stack
3. Support +, -, *, / operators and return float result

Need to handle operator precedence: *, / before +, -.
Use two stacks: one for numbers, one for operators.
Process parentheses recursively.

def evaluate_expression(expression):
    def precedence(op):
        if op in ['+', '-']:
            return 1
        if op in ['*', '/']:
            return 2
        return 0
    
    def apply_operator(operators, values):
        operator = operators.pop()
        right = values.pop()
        left = values.pop()
        
        if operator == '+':
            values.append(left + right)
        elif operator == '-':
            values.append(left - right)
        elif operator == '*':
            values.append(left * right)
        elif operator == '/':
            if right == 0:
                return None
            values.append(left / right)
    
    expression = expression.replace(' ', '')
    values = []
    operators = []
    i = 0
    
    while i < len(expression):
        if expression[i].isdigit() or expression[i] == '.':
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            values.append(float(expression[i:j]))
            i = j
        elif expression[i] == '(':
            operators.append(expression[i])
            i += 1
        elif expression[i] == ')':
            while operators and operators[-1] != '(':
                if apply_operator(operators, values) is None:
                    return None
            operators.pop()
            i += 1
        elif expression[i] in ['+', '-', '*', '/']:
            while (operators and operators[-1] != '(' and
                   precedence(operators[-1]) >= precedence(expression[i])):
                if apply_operator(operators, values) is None:
                    return None
            operators.append(expression[i])
            i += 1
        else:
            i += 1
    
    while operators:
        if apply_operator(operators, values) is None:
            return None
    
    return values[0] if values else None

                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "knapsack" in user.lower():
                code = """# PLAN
1. Implement 0/1 Knapsack using dynamic programming
2. Create 2D DP table: dp[i][w] = max value with first i items, weight limit w
3. Handle edge cases: no items, zero capacity

For each item, decide whether to include it or not.
dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + value[i])
Base case: dp[0][w] = 0 for all w.

def knapsack_01(items, capacity):
    if not items or capacity <= 0:
        return 0
    
    n = len(items)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        weight, value = items[i-1]
        for w in range(1, capacity + 1):
            if weight <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value)
            else:
                dp[i][w] = dp[i-1][w]
    
    return dp[n][capacity]

                return Completion(text=code, latency_s=self.mock_latency)
        
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
                        code = f"""{imports}{func_signature}
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False"""
                    
                    elif 'separate_paren_groups' in func_name:
                        code = f"""{imports}{func_signature}
    result = []
    current_string = []
    current_depth = 0
    
    for c in paren_string:
        if c == '(':
            current_depth += 1
            current_string.append(c)
        elif c == ')':
            current_depth -= 1
            current_string.append(c)
            
            if current_depth == 0:
                result.append(''.join(current_string))
                current_string.clear()
    
    return result"""
                    
                    elif 'truncate_number' in func_name:
                        code = f"{imports}{func_signature}\n    return number % 1.0"
                    
                    else:
                        code = f"{imports}{func_signature}\n    pass  # Mock implementation"
                    
                    return Completion(text=code, latency_s=self.mock_latency)
        
        elif 'shared elements' in user.lower():
            code = """def similar_elements(test_tup1, test_tup2):
    res = tuple(set(test_tup1) & set(test_tup2))
    return res"""
            return Completion(text=code, latency_s=self.mock_latency)
        
        elif 'non-prime' in user.lower() or 'not prime' in user.lower():
            code = """import math
def is_not_prime(n):
    if n <= 1:
        return True
    if n == 2:
        return False
    result = False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
            break
    return result"""
            return Completion(text=code, latency_s=self.mock_latency)
        
        return Completion(
            text="# Mock response - implement the requested function",
            latency_s=self.mock_latency
        )
