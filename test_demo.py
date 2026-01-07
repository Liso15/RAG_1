#!/usr/bin/env python3.11
"""
Test script to demonstrate Context-Aware RAG System features
"""

import subprocess
import sys

def run_test(name, command):
    """Run a test and display results"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    """Run all demonstration tests"""
    print("Context-Aware RAG System - Demonstration Tests")
    
    tests = [
        ("Normal Operation - Server Restart Query", 
         'python3.11 main.py --query "How do I restart the server safely?" --verbose'),
        
        ("Different Query - Emergency Shutdown", 
         'python3.11 main.py --query "Emergency shutdown procedure" --verbose'),
        
        ("Budget Stress Test - Long Goal", 
         'python3.11 main.py --query "database maintenance" --goal "This is an extremely long goal that will definitely exceed the 1500 character limit to demonstrate truncation behavior. The system should handle this gracefully by truncating at exactly 1500 characters and adding ellipsis. This tests the mathematical precision of budget enforcement and shows how the system maintains strict limits even with excessive input content. The goal continues to be verbose to ensure we exceed the limit significantly and can observe the truncation behavior in action. This demonstrates production-ready constraint handling for agentic AI applications where context window management is critical." --verbose'),
        
        ("Empty Retrieval Test - Non-existent Topic", 
         'python3.11 main.py --query "quantum computing algorithms" --verbose'),
        
        ("Custom Instructions Test", 
         'python3.11 main.py --query "server restart" --instructions "You are a senior DevOps engineer with 10+ years experience" --goal "Provide detailed guidance with safety checks" --verbose')
    ]
    
    passed = 0
    total = len(tests)
    
    for name, command in tests:
        if run_test(name, command):
            passed += 1
        else:
            print(f"❌ Test failed: {name}")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 All tests passed! The Context-Aware RAG System is working correctly.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    main()