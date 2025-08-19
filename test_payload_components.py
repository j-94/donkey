#!/usr/bin/env python3
"""
Test individual payload components for validation
"""

def test_engine_initialization():
    """Test that the payload engine initializes correctly"""
    try:
        from interpretable_symbiosis_payload import InterpretableSymbiosisEngine
        engine = InterpretableSymbiosisEngine()
        print("✅ Engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        return False

def test_integration_initialization():
    """Test that the integration component initializes correctly"""
    try:
        from payload_alignment_integration import PayloadAlignmentIntegration
        integration = PayloadAlignmentIntegration()
        print("✅ Integration initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Integration initialization failed: {e}")
        return False

def test_basic_payload_execution():
    """Test basic payload execution loop"""
    try:
        from interpretable_symbiosis_payload import InterpretableSymbiosisEngine
        
        engine = InterpretableSymbiosisEngine()
        test_brief = "Simple test task"
        
        result = engine.run_payload_execution_loop(test_brief)
        
        if result.get('success'):
            print("✅ Basic payload execution successful")
            return True
        else:
            print(f"❌ Basic payload execution failed: {result.get('message', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Basic payload execution error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Payload Components...")
    print("=" * 40)
    
    tests = [
        test_engine_initialization,
        test_integration_initialization,
        test_basic_payload_execution
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All component tests passed!")
    else:
        print("🚨 Some tests failed - check implementation")
