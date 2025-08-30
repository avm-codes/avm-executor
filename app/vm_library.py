import uuid
import json
import time
import random
import os
import requests
from typing import Dict, Any, Optional

class AVMLibrary:
    """
    AVM library that calls the real VM API endpoints.
    """
    
    def __init__(self):
        self.vm_ip = os.getenv('VM_IP', 'localhost')
        self.vm_port = os.getenv('VM_PORT', '8080')
        self.base_url = f"http://{self.vm_ip}:{self.vm_port}"
    
    def acquire(self) -> str:
        """
        Acquire a new VM instance and return its ID.
        
        Returns:
            str: A unique VM ID
        """
        try:
            # Call the real VM API
            response = requests.post(f"{self.base_url}/acquire")
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            vm_id = data.get('vm_id')
            
            if not vm_id:
                raise ValueError("No VM ID returned from API")
            
            print(f"[REAL] Acquired VM with ID: {vm_id}")
            return vm_id
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to acquire VM: {e}")
            raise e
    
    def exec(self, vm_id: str, language: str, code: str) -> Dict[str, Any]:
        """
        Execute code on a specific VM instance.
        
        Args:
            vm_id (str): The VM ID to execute code on
            language (str): Programming language (python, typescript, php)
            code (str): The code to execute
            
        Returns:
            Dict[str, Any]: Execution results with stdout and stderr
        """
        try:
            # Prepare the request payload
            payload = {
                "vm_id": vm_id,
                "exec_args": {
                    "code": code,
                    "language": language
                }
            }
            
            # Call the VM API
            response = requests.post(f"{self.base_url}/exec", json=payload)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract the body which contains the execution result
            body_str = data.get('body', '{}')
            body_data = json.loads(body_str)
            
            # Build the result object
            result = {
                "vm_id": vm_id,
                "stdout": body_data.get('stdout', ''),
                "stderr": body_data.get('error', ''),
                "execution_time": body_data.get('execution_time_seconds', 0),
                "status": response.status_code
            }
            
            print(f"[REAL] Executed code on VM {vm_id} ({language})")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to execute code on VM {vm_id}: {e}")
            raise e
    
    def release(self, vm_id: str) -> Dict[str, Any]:
        """
        Release/kill a VM instance.
        
        Args:
            vm_id (str): The VM ID to release
            
        Returns:
            Dict[str, Any]: Release response
        """
        try:
            # Prepare the request payload
            payload = {
                "vm_id": vm_id
            }
            
            # Call the VM API
            response = requests.post(f"{self.base_url}/kill", json=payload)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            print(f"[REAL] Released VM with ID: {vm_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to release VM {vm_id}: {e}")
            raise e


# Global instance for easy access
vm_library = AVMLibrary()

# Convenience functions to match expected API
def acquire() -> str:
    """Convenience function to acquire a VM"""
    return vm_library.acquire()

def exec(vm_id: str, language: str, code: str) -> Dict[str, Any]:
    """Convenience function to execute code on a VM"""
    return vm_library.exec(vm_id, language, code)

def release(vm_id: str) -> Dict[str, Any]:
    """Convenience function to release a VM"""
    return vm_library.release(vm_id) 