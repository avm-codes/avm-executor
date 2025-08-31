from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

from ..vm_library import exec as vm_exec, release
from ..vm_pool import get_vm_from_pool

class BaseExecutor(ABC):
    EXECUTION_TIMEOUT = 360

    @abstractmethod
    def get_dependencies(self, code: str) -> List[str]:
        """Analyzes the code and returns the required dependencies"""
        pass

    @abstractmethod
    def install_dependencies(self, dependencies: List[str]):
        """Installs dependencies in the virtual environment"""
        pass

    @abstractmethod
    def _get_file_extension(self) -> str:
        """Returns the file extension for the specific language"""
        pass

    @abstractmethod
    def _prepare_code(self, code: str, inputs: Dict[str, Any], env_vars: Dict[str, str]) -> str:
        """Prepares the code by adding input and environment variables"""
        pass

    @abstractmethod
    def _process_output(self, stdout: str) -> tuple[str, Dict[str, Any]]:
        """Processes the stdout to extract both regular output and the result object"""
        pass

    def execute(self, code: str, language: str, dependencies: List[str] = None, inputs: Dict[str, Any] = None, env_vars: Dict[str, str] = None, execution_timeout: int = EXECUTION_TIMEOUT) -> Dict[str, Any]:
        """Executes the code and returns the result"""
        vm_id = None
        try:
            # Get a VM from pool
            vm_id = get_vm_from_pool()
            
            if not vm_id:
                raise Exception("Failed to get VM from pool")

            if not dependencies:
                dependencies = self.get_dependencies(code)

            prepared_code = self._prepare_code(code, inputs or {}, env_vars or {})

            if dependencies:
                logger.info(f"Dependencies found: {dependencies}. Using a virtual environment.")
                self.install_dependencies(dependencies)
            else:
                logger.info("No dependencies detected. Executing code directly.")
            
            # Execute code
            result = vm_exec(vm_id, language, prepared_code)

            stdout_raw = result.get("stdout", "")
            stderr_raw = result.get("stderr", "")
            execution_time = result.get("execution_time", 0)

            stdout, output_data = self._process_output(stdout_raw)

            return {
                "stdout": stdout,
                "output": output_data,
                "execution_time_seconds": execution_time,
                "error": stderr_raw if stderr_raw else None,
                "vm_id": vm_id
            }

        except Exception as e:
            return { "error": str(e) }
        finally:
            # Release the VM
            if vm_id:
                release(vm_id)