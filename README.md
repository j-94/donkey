# CSCE v2.3 Dialogic Metaprogramming Evaluation System

A comprehensive evaluation framework for testing the CSCE (Cognitive State Control Engine) v2.3 Dialogic Metaprogramming system against vanilla code generation approaches, with full GPT-5 integration and compatibility analysis.

## Overview

This repository contains the complete implementation and evaluation of the CSCE v2.3 Dialogic Metaprogramming system, including:

- **GPT-5 Integration**: Support for both `gpt-5-mini-2025-08-07` and `gpt-5-2025-08-07` models
- **Comprehensive Test Suite**: Complex algorithmic problems designed to benefit from structured thinking
- **Compatibility Analysis**: Detailed analysis of GPT-5 complexity threshold issues
- **Mock Testing Infrastructure**: Fallback testing when API quotas are limited
- **EvalPlus Integration**: HumanEval+ and MBPP+ dataset evaluation capabilities

## Key Findings

### GPT-5 Compatibility Issues
Both GPT-5 models (`gpt-5-mini-2025-08-07` and `gpt-5-2025-08-07`) return **empty responses** when given the full CSCE v2.3 system prompt due to complexity threshold issues:

- **Full CSCE v2.3**: 0% success rate (empty responses)
- **Simplified CSCE**: 67% success rate with structured thinking
- **Vanilla**: 100% success rate (basic implementations)

### System Complexity Analysis
The full CSCE v2.3 system prompt contains:
- 3,793 characters with dense technical content
- 19 Greek symbols (Ψ, π, Γ, λ, ω, β, ε)
- Complex metacognitive simulation requirements
- Multi-layered tool protocols and state management

## Core Components

### Model Clients
- `model_client_clean.py` - Clean OpenAI API client with GPT-5 parameter handling
- `simple_mock_client.py` - Mock client for testing without API calls

### CSCE System
- `csce_generator.py` - CSCE v2.3 Dialogic Metaprogramming implementation
- `csce_kernel.py` - CSCE research kernel with metacognitive control
- `vanilla_generator.py` - Baseline vanilla code generation

### Evaluation Framework
- `comprehensive_test_suite.py` - Complex algorithmic problems test suite
- `run_evalplus_csce.py` - EvalPlus integration for HumanEval+/MBPP+ evaluation
- `test_csce_v23.py` - Basic CSCE v2.3 functionality tests

### Analysis Tools
- `csce_complexity_analysis.py` - Detailed prompt complexity analysis
- `diagnose_csce_hanging.py` - GPT-5 compatibility diagnostics
- `test_working_csce_alternative.py` - Simplified CSCE testing

## Quick Start

### Prerequisites
```bash
pip install openai
export OPENAI_API="your-api-key-here"
```

### Basic Testing
```bash
# Test GPT-5 accessibility
python test_gpt5_access.py

# Run CSCE v2.3 basic test
python test_csce_v23.py

# Run comprehensive test suite (mock mode)
python comprehensive_test_suite.py --mock
```

### Full Evaluation
```bash
# Run EvalPlus evaluation with CSCE vs vanilla comparison
python run_evalplus_csce.py

# Run comprehensive algorithmic problems test
python comprehensive_test_suite.py
```

## Test Problems

The comprehensive test suite includes 5 complex algorithmic problems:

1. **Longest Increasing Subsequence** - Dynamic programming approach
2. **LRU Cache Implementation** - Data structure design with doubly linked list
3. **Dijkstra's Shortest Path** - Graph algorithms with priority queue
4. **Mathematical Expression Evaluator** - Parsing and computation with operator precedence
5. **0/1 Knapsack Problem** - Optimization with dynamic programming

## Results Summary

### Mock Testing (System Structure Validation)
- **CSCE v2.3**: Generates comprehensive implementations with proper STATE_SIG format
- **Vanilla**: Generates only placeholder functions
- **Success Rate**: 100% for both (demonstrates system structure)

### Real GPT-5 Testing
- **GPT-5 with Full CSCE**: 0% success (empty responses due to complexity)
- **GPT-5 with Simplified CSCE**: 67% success with structured thinking
- **GPT-5 with Vanilla**: 100% success (basic implementations)

### EvalPlus Evaluation (50 HumanEval+ problems)
- **Vanilla GPT-4o**: 87.2% pass@1
- **CSCE v2.3 GPT-4o**: 86.0% pass@1 (with structured STATE_SIG metadata)

## STATE_SIG Format

All CSCE responses include metacognitive state tracking:
```python
# STATE_SIG: {"steps":<int>,"uncertainty":<0..1>,"sec_left":<int>,"spec_ok":<bool>}
```

## Documentation

- `gpt5_final_evaluation_summary.md` - Complete GPT-5 integration analysis
- `csce_v23_evaluation_results.md` - Comprehensive evaluation results
- `comprehensive_test_results.json` - Detailed test outcomes
- `gpt5_integration_summary.md` - GPT-5 specific integration details

## Recommendations

1. **Use Simplified CSCE for GPT-5** - Maintains structured thinking without complexity overload
2. **Test Full CSCE with Other Models** - GPT-4o, Claude may handle complete system better
3. **Consider CSCE v2.4 Development** - GPT-5 compatible version with reduced complexity

## Repository Structure

```
├── README.md                           # This file
├── model_client_clean.py              # Clean OpenAI API client
├── csce_generator.py                   # CSCE v2.3 implementation
├── comprehensive_test_suite.py         # Complex problems test suite
├── test_csce_v23.py                   # Basic functionality tests
├── csce_complexity_analysis.py        # Complexity analysis tools
├── gpt5_final_evaluation_summary.md   # Complete analysis
├── comprehensive_test_results.json    # Test outcomes
└── [additional evaluation files...]
```

## Contributing

This evaluation framework is designed for research into metacognitive code generation systems. The infrastructure supports:

- Easy addition of new test problems
- Integration with different model APIs
- Extensible evaluation metrics
- Mock testing for development without API costs

## License

Research and evaluation framework for CSCE v2.3 Dialogic Metaprogramming system.

---

**Link to Devin run**: https://app.devin.ai/sessions/9983a91b3f2a4bb999bb277cec2dbb95  
**Requested by**: @j-94
