"""
Detailed analysis of CSCE v2.3 prompt complexity and simplified alternative
"""

from csce_generator import CSCE_SYSTEM_PROMPT, create_csce_prompt

def analyze_prompt_complexity():
    """Analyze the complexity metrics of CSCE v2.3 vs simplified version"""
    
    print("=== CSCE v2.3 COMPLEXITY ANALYSIS ===\n")
    
    print("1. SYSTEM PROMPT ANALYSIS:")
    print(f"   Length: {len(CSCE_SYSTEM_PROMPT)} characters")
    print(f"   Lines: {len(CSCE_SYSTEM_PROMPT.split(chr(10)))} lines")
    
    greek_symbols = ['Ψ', 'π', 'Γ', 'λ', 'ω', 'β', 'ε']
    greek_count = sum(CSCE_SYSTEM_PROMPT.count(symbol) for symbol in greek_symbols)
    print(f"   Greek symbols: {greek_count} occurrences")
    
    technical_terms = ['argmax', 'metacognitive', 'DoD-TETHER', 'VERIFY GRID', 'SELF_CALL', 'micro-step']
    tech_count = sum(CSCE_SYSTEM_PROMPT.count(term) for term in technical_terms)
    print(f"   Technical jargon terms: {tech_count} occurrences")
    
    sample_payload = create_csce_prompt("test_func", "a, b", "Test problem", 30)
    print(f"\n2. PAYLOAD COMPLEXITY:")
    print(f"   Total payload length: {len(sample_payload)} characters")
    print(f"   JSON structure depth: ~4 levels (nested objects)")
    print(f"   Number of fields: ~15 top-level + nested fields")
    
    print(f"\n3. MOST PROBLEMATIC SECTIONS:")
    
    problematic_sections = [
        "KEY OBJECTS (internal)",
        "ARGMAX ACTION SELECTION", 
        "SELF-CALL (bounded self-simulation)",
        "TOOL I/O PROTOCOL",
        "BUDGET LOOP (pseudo)"
    ]
    
    for section in problematic_sections:
        if section in CSCE_SYSTEM_PROMPT:
            start = CSCE_SYSTEM_PROMPT.find(section)
            end = CSCE_SYSTEM_PROMPT.find('\n\n', start)
            if end == -1:
                end = start + 200
            excerpt = CSCE_SYSTEM_PROMPT[start:end]
            print(f"   - {section}: {len(excerpt)} chars")
    
    print(f"\n4. SIMPLIFIED ALTERNATIVE:")
    
    simplified_csce = """You are a structured Python code generator that thinks step by step.

For each coding problem:
1. PLAN: Break down the problem into logical steps
2. THINK: Consider the approach, edge cases, and implementation details  
3. IMPLEMENT: Write clean, working Python code
4. VERIFY: Check that the solution meets requirements

Output format:
- Only Python code, no markdown fences
- Include planning as comments at the top
- End with: # STATE_SIG: {"steps":<int>,"uncertainty":<0..1>,"sec_left":<int>,"spec_ok":<bool>}

Focus on correctness and clarity."""
    
    print(f"   Length: {len(simplified_csce)} characters ({len(simplified_csce)/len(CSCE_SYSTEM_PROMPT)*100:.1f}% of original)")
    print(f"   Lines: {len(simplified_csce.split(chr(10)))} lines")
    print(f"   Greek symbols: 0")
    print(f"   Technical jargon: Minimal")
    print(f"   Cognitive load: Low (linear instructions)")
    
    print(f"\n5. KEY DIFFERENCES:")
    print("   ✓ Simplified: Linear PLAN→THINK→IMPLEMENT→VERIFY flow")
    print("   ✗ Original: Complex metacognitive simulation with state management")
    print("   ✓ Simplified: Plain English instructions")
    print("   ✗ Original: Greek symbols and mathematical notation")
    print("   ✓ Simplified: Simple comment-based output format")
    print("   ✗ Original: Complex tool protocols and XML-like tags")
    print("   ✓ Simplified: Clear, actionable steps")
    print("   ✗ Original: Abstract concepts like 'argmax over candidates'")
    
    return simplified_csce

def create_working_csce_v23():
    """Create a GPT-5-mini compatible version of CSCE v2.3"""
    
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
        """Simplified payload that works with GPT-5-mini"""
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
    
    return working_system, create_working_payload

if __name__ == "__main__":
    simplified = analyze_prompt_complexity()
    
    print(f"\n=== SIMPLIFIED CSCE v2.3 SYSTEM PROMPT ===")
    print(simplified)
    
    working_system, working_payload_func = create_working_csce_v23()
    print(f"\n=== WORKING CSCE v2.3 ALTERNATIVE ===")
    print(working_system)
    
    sample_working_payload = working_payload_func("add_numbers", "a, b", "Write a function that adds two numbers")
    print(f"\n=== WORKING PAYLOAD EXAMPLE ===")
    print(sample_working_payload)
