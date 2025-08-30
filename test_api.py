#!/usr/bin/env python3
"""
Test script for the AVM API server
"""

import requests
import json
import time

def test_health():
    """Test health endpoint"""
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get("http://localhost:8080/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_execute_python():
    """Test Python code execution"""
    print("\n=== Testing Python Execution ===")
    
    # Test basic code
    data = {
        "language": "python",
        "code": "print('Hello, World!')"
    }
    
    try:
        response = requests.post("http://localhost:8080/execute", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_execute_with_input():
    """Test execution with input variables"""
    print("\n=== Testing Execution with Input ===")
    
    data = {
        "language": "python",
        "code": "print(f'Hello {name}!')",
        "input": {
            "name": "AVM"
        }
    }
    
    try:
        response = requests.post("http://localhost:8080/execute", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_execute_with_output():
    """Test execution with structured output"""
    print("\n=== Testing Execution with Output ===")
    
    data = {
        "language": "python",
        "code": "print('Processing...')\noutput = {'result': 42, 'status': 'success'}"
    }
    
    try:
        response = requests.post("http://localhost:8080/execute", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_multiple_executions():
    """Test multiple executions to see random success/error"""
    print("\n=== Testing Multiple Executions ===")
    
    for i in range(5):
        print(f"\nExecution {i+1}:")
        data = {
            "language": "python",
            "code": f"print('Test execution {i+1}')"
        }
        
        try:
            response = requests.post("http://localhost:8080/execute", json=data)
            result = response.json()
            status = "✅ Success" if not result.get("error") else "❌ Error"
            print(f"  {status}: {result.get('stdout', '').strip() or result.get('error', '')}")
        except Exception as e:
            print(f"  Error: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing AVM API Server")
    print("=" * 50)
    
    # Wait a bit for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_health()
    test_execute_python()
    test_execute_with_input()
    test_execute_with_output()
    test_multiple_executions()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
