from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import tempfile
import os
import subprocess
import time
import logging
import json

logger = logging.getLogger(__name__)

class BaseExecutor(ABC):
    EXECUTION_TIMEOUT = 360

    @abstractmethod
    def get_dependencies(self, code: str) -> List[str]:
        """Analyzes the code and returns the required dependencies"""
        pass

    @abstractmethod
    def install_dependencies(self, dependencies: List[str], venv_path: str):
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
    def _execute_directly(self, code_file_path: str, inputs: Dict[str, Any], env_vars: Dict[str, str], execution_timeout: int) -> subprocess.CompletedProcess:
        """Executes the code without dependencies"""
        pass

    @abstractmethod
    def _execute_with_dependencies(self, code_file_path: str, dependencies: List[str], inputs: Dict[str, Any], env_vars: Dict[str, str], execution_timeout: int) -> subprocess.CompletedProcess:
        """Executes the code with installed dependencies"""
        pass

    @abstractmethod
    def _process_output(self, stdout: str) -> tuple[str, Dict[str, Any]]:
        """Processes the stdout to extract both regular output and the result object"""
        pass

    def execute(self, code: str, dependencies: List[str] = None, inputs: Dict[str, Any] = None, env_vars: Dict[str, str] = None, execution_timeout: int = EXECUTION_TIMEOUT) -> Dict[str, Any]:
        """Executes the code and returns the result"""
        try:
            start_time = time.time()
            if not dependencies:
                dependencies = self.get_dependencies(code)
            else:
                code_dependencies = self.get_dependencies(code)
                dependencies = list(set(dependencies + code_dependencies))

            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension()) as code_file:
                code_file_path = code_file.name
                prepared_code = self._prepare_code(code, inputs or {}, env_vars or {})
                with open(code_file_path, 'w') as f:
                    f.write(prepared_code)

            if not dependencies:
                logger.info("No dependencies detected. Executing code directly.")
                result = self._execute_directly(code_file_path, inputs or {}, env_vars or {}, execution_timeout)
            else:
                logger.info(f"Dependencies found: {dependencies}. Using a virtual environment.")
                result = self._execute_with_dependencies(code_file_path, dependencies, inputs or {}, env_vars or {}, execution_timeout)

            os.remove(code_file_path)
            stdout, output_data = self._process_output(result.stdout)

            return {
                "stdout": stdout,
                "output": output_data,
                "execution_time_seconds": time.time() - start_time,
                "error": result.stderr if result.stderr else None
            }

        except subprocess.TimeoutExpired:
            return {"error": f"Execution timed out. Max {execution_timeout} seconds"}
        except Exception as e:
            return {
                "error": str(e),
                "execution_time_seconds": time.time() - start_time
            }
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f'Execution time: {execution_time:.2f} seconds') 