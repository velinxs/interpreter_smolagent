"""
Test script for the EnhancedPythonInterpreter.
"""

from enhanced_python import EnhancedPythonInterpreter

def main():
    # Create an instance of the EnhancedPythonInterpreter
    interpreter = EnhancedPythonInterpreter()
    
    # Test basic Python execution
    print("Testing basic Python execution...")
    result = interpreter.forward("2 + 2")
    print(result)
    
    # Test file operations
    print("\nTesting file operations...")
    result = interpreter.forward("""
import os
with open('test_file.txt', 'w') as f:
    f.write('Hello from EnhancedPythonInterpreter!')
os.path.exists('test_file.txt')
""")
    print(result)
    
    # Test shell commands
    print("\nTesting shell commands...")
    result = interpreter.forward("""
import subprocess
result = subprocess.run(['ls', '-la'], capture_output=True, text=True)
result.stdout
""")
    print(result)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()