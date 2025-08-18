"""
Simple mock client for testing CSCE v2.3 without API calls
"""

import time
from dataclasses import dataclass

@dataclass
class Completion:
    text: str
    latency_s: float

class SimpleMockClient:
    def __init__(self, mock_latency: float = 0.1):
        self.mock_latency = mock_latency

    def complete(self, system: str, user: str, temperature: float = 0.0, max_tokens: int = 512) -> Completion:
        time.sleep(self.mock_latency)
        
        if "CSCE_PAYLOAD" in user and "Dialogic Metaprogramming" in system:
            if "sum_evens" in user.lower():
                code = "def sum_evens(numbers):\n    return sum(num for num in numbers if num % 2 == 0)\n\n# STATE_SIG: {\"steps\":2,\"uncertainty\":0.1,\"sec_left\":28,\"spec_ok\":true}"
                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "longest_increasing_subsequence" in user.lower():
                code = "def longest_increasing_subsequence(nums):\n    if not nums:\n        return 0\n    n = len(nums)\n    dp = [1] * n\n    for i in range(1, n):\n        for j in range(i):\n            if nums[j] < nums[i]:\n                dp[i] = max(dp[i], dp[j] + 1)\n    return max(dp)\n\n# STATE_SIG: {\"steps\":3,\"uncertainty\":0.2,\"sec_left\":25,\"spec_ok\":true}"
                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "lrucache" in user.lower():
                code = "class LRUCache:\n    def __init__(self, capacity):\n        self.capacity = capacity\n        self.cache = {}\n        self.head = self.Node(0, 0)\n        self.tail = self.Node(0, 0)\n        self.head.next = self.tail\n        self.tail.prev = self.head\n    \n    class Node:\n        def __init__(self, key, val):\n            self.key = key\n            self.val = val\n            self.prev = None\n            self.next = None\n    \n    def get(self, key):\n        if key in self.cache:\n            node = self.cache[key]\n            self._remove(node)\n            self._add(node)\n            return node.val\n        return -1\n    \n    def put(self, key, value):\n        if key in self.cache:\n            self._remove(self.cache[key])\n        node = self.Node(key, value)\n        self._add(node)\n        self.cache[key] = node\n        if len(self.cache) > self.capacity:\n            lru = self.head.next\n            self._remove(lru)\n            del self.cache[lru.key]\n    \n    def _add(self, node):\n        prev_node = self.tail.prev\n        prev_node.next = node\n        node.prev = prev_node\n        node.next = self.tail\n        self.tail.prev = node\n    \n    def _remove(self, node):\n        prev_node = node.prev\n        next_node = node.next\n        prev_node.next = next_node\n        next_node.prev = prev_node\n\n# STATE_SIG: {\"steps\":4,\"uncertainty\":0.1,\"sec_left\":20,\"spec_ok\":true}"
                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "dijkstra" in user.lower():
                code = "import heapq\n\ndef dijkstra_shortest_path(graph, source):\n    if not graph:\n        return {}\n    \n    distances = {vertex: float('inf') for vertex in graph}\n    distances[source] = 0\n    pq = [(0, source)]\n    \n    while pq:\n        current_dist, current_vertex = heapq.heappop(pq)\n        \n        if current_dist > distances[current_vertex]:\n            continue\n        \n        for neighbor, weight in graph.get(current_vertex, []):\n            distance = current_dist + weight\n            \n            if distance < distances[neighbor]:\n                distances[neighbor] = distance\n                heapq.heappush(pq, (distance, neighbor))\n    \n    return distances\n\n# STATE_SIG: {\"steps\":3,\"uncertainty\":0.15,\"sec_left\":22,\"spec_ok\":true}"
                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "evaluate_expression" in user.lower():
                code = "def evaluate_expression(expression):\n    def precedence(op):\n        if op in ['+', '-']:\n            return 1\n        if op in ['*', '/']:\n            return 2\n        return 0\n    \n    def apply_operator(operators, values):\n        operator = operators.pop()\n        right = values.pop()\n        left = values.pop()\n        \n        if operator == '+':\n            values.append(left + right)\n        elif operator == '-':\n            values.append(left - right)\n        elif operator == '*':\n            values.append(left * right)\n        elif operator == '/':\n            if right == 0:\n                return None\n            values.append(left / right)\n    \n    expression = expression.replace(' ', '')\n    values = []\n    operators = []\n    i = 0\n    \n    while i < len(expression):\n        if expression[i].isdigit() or expression[i] == '.':\n            j = i\n            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):\n                j += 1\n            values.append(float(expression[i:j]))\n            i = j\n        elif expression[i] == '(':\n            operators.append(expression[i])\n            i += 1\n        elif expression[i] == ')':\n            while operators and operators[-1] != '(':\n                if apply_operator(operators, values) is None:\n                    return None\n            operators.pop()\n            i += 1\n        elif expression[i] in ['+', '-', '*', '/']:\n            while (operators and operators[-1] != '(' and\n                   precedence(operators[-1]) >= precedence(expression[i])):\n                if apply_operator(operators, values) is None:\n                    return None\n            operators.append(expression[i])\n            i += 1\n        else:\n            i += 1\n    \n    while operators:\n        if apply_operator(operators, values) is None:\n            return None\n    \n    return values[0] if values else None\n\n# STATE_SIG: {\"steps\":4,\"uncertainty\":0.25,\"sec_left\":18,\"spec_ok\":true}"
                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "knapsack" in user.lower():
                code = "def knapsack_01(items, capacity):\n    if not items or capacity <= 0:\n        return 0\n    \n    n = len(items)\n    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]\n    \n    for i in range(1, n + 1):\n        weight, value = items[i-1]\n        for w in range(1, capacity + 1):\n            if weight <= w:\n                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value)\n            else:\n                dp[i][w] = dp[i-1][w]\n    \n    return dp[n][capacity]\n\n# STATE_SIG: {\"steps\":3,\"uncertainty\":0.1,\"sec_left\":24,\"spec_ok\":true}"
                return Completion(text=code, latency_s=self.mock_latency)
            
            elif "kadane" in user.lower() or "maximum sum" in user.lower() or "contiguous subarray" in user.lower():
                code = "def max_subarray_sum(arr):\n    if not arr:\n        return 0\n    \n    max_sum = current_sum = arr[0]\n    \n    for num in arr[1:]:\n        current_sum = max(num, current_sum + num)\n        max_sum = max(max_sum, current_sum)\n    \n    return max_sum\n\n# STATE_SIG: {\"steps\":2,\"uncertainty\":0.1,\"sec_left\":27,\"spec_ok\":true}"
                return Completion(text=code, latency_s=self.mock_latency)
            
            else:
                code = "def placeholder():\n    pass\n\n# STATE_SIG: {\"steps\":1,\"uncertainty\":0.5,\"sec_left\":29,\"spec_ok\":false}"
                return Completion(text=code, latency_s=self.mock_latency)
        
        return Completion(text="def placeholder(): pass", latency_s=self.mock_latency)
