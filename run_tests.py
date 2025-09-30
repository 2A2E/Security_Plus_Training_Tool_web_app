#!/usr/bin/env python3
"""
Test runner script for Security Plus Training Tool
"""
import sys
import subprocess
import os

def run_tests():
    """Run the test suite with appropriate options"""
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Test command
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    # Add coverage if available
    try:
        import coverage
        cmd.extend(['--cov=.', '--cov-report=term-missing'])
    except ImportError:
        print("Coverage not available. Install with: pip install coverage")
    
    print("Running tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the tests
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    run_tests()
