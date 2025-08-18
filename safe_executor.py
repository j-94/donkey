"""
Safe code execution harness with proper isolation
"""

import tempfile
import subprocess
import sys
import os
import textwrap
import time
import pathlib
import traceback
from typing import Tuple

class SafeCodeExecutor:
    """Executes code safely in isolated environment with proper test separation"""
    
    def __init__(self, timeout_seconds: int = 10):
        self.timeout = timeout_seconds
    
    def run(self, candidate_code: str, test_code: str, entry_point: str) -> Tuple[bool, str, str, float, bool, bool]:
        """
        Execute candidate code against test code in isolated environment
        
        Args:
            candidate_code: The generated solution code
            test_code: Test assertions to validate the solution
            entry_point: Name of the main function to test
            
        Returns:
            (success, stdout, stderr, execution_time, compile_pass, entry_point_error)
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            candidate_path = temp_path / "candidate.py"
            test_path = temp_path / "test_runner.py"
            
            candidate_path.write_text(candidate_code)
            
            compile_pass = True
            entry_point_error = False
            
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("candidate", str(candidate_path))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                
                has_entry = hasattr(mod, entry_point)
                if not has_entry:
                    entry_point_error = True
                    available_funcs = [n for n in dir(mod) if callable(getattr(mod, n)) and not n.startswith('_')]
                    error_msg = f"Missing entry point: {entry_point}. Found: {available_funcs}"
                    return False, "", error_msg, 0.0, compile_pass, entry_point_error
                    
            except Exception as e:
                compile_pass = False
                error_msg = f"Import error: {e}\n{traceback.format_exc()}"
                return False, "", error_msg, 0.0, compile_pass, entry_point_error
            
            test_runner_code = textwrap.dedent(f"""
import sys
import importlib.util
import traceback

try:
    spec = importlib.util.spec_from_file_location("candidate", "candidate.py")
    candidate_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate_module)
    
    globals()['{entry_point}'] = getattr(candidate_module, '{entry_point}')
    
    exec('''
{test_code}
''')
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Test failed: {{e}}")
    traceback.print_exc()
    sys.exit(1)
""")
            
            test_path.write_text(test_runner_code)
            
            start_time = time.time()
            try:
                process = subprocess.run(
                    [sys.executable, str(test_path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir
                )
                execution_time = time.time() - start_time
                
                success = (process.returncode == 0)
                return success, process.stdout, process.stderr, execution_time, compile_pass, entry_point_error
                
            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                return False, "", f"Execution timed out after {self.timeout}s", execution_time, compile_pass, entry_point_error
            
            except Exception as e:
                execution_time = time.time() - start_time
                return False, "", f"Execution error: {str(e)}", execution_time, compile_pass, entry_point_error
