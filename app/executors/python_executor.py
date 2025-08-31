import ast
import sys
import json
from typing import List, Dict, Any
from .base import BaseExecutor


class PythonExecutor(BaseExecutor):
    def get_dependencies(self, code: str) -> List[str]:
        tree = ast.parse(code)
        dependencies = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                dependencies.add(node.module.split('.')[0])
        
        built_in_modules = set(sys.builtin_module_names)
        standard_lib_modules = getattr(sys, "stdlib_module_names", built_in_modules)
        
        return [dep for dep in dependencies if dep not in standard_lib_modules]

    def install_dependencies(self, dependencies: List[str]):
        if not dependencies:
            return
        
        for dep in dependencies:
            pass # TODO: Implement pip install by using the vm_library

    def _get_file_extension(self) -> str:
        return ".py"

    def _prepare_code(self, code: str, inputs: Dict[str, Any], env_vars: Dict[str, str]) -> str:
        """Prepares the Python code by adding input and environment variables"""
        
        env_code = "\n".join([f"os.environ['{k}'] = '{v}'" for k, v in env_vars.items()])
        if env_code:
            code = f"import os\nimport json\nimport logging\nlogging.basicConfig(level=logging.ERROR)\n{env_code}\n{code}"
        else:
            code = f"import json\nimport logging\nlogging.basicConfig(level=logging.ERROR)\n{code}"

        input_code = "\n".join([f"{k} = {repr(v)}" for k, v in inputs.items()])
        if input_code:
            code = f"{input_code}\n{code}"

        code += """
# Wrapper to manage the result
result = None
try:
    if 'output' in locals():
        result = output
except Exception as e:
    print(f'Error capturing result: {e}', file=sys.stderr)

# Output in JSON format
print('__RESULT_START__')
print(json.dumps(result))
print('__RESULT_END__')
"""
        return code



    def _process_output(self, stdout: str) -> tuple[str, Dict[str, Any]]:
        """Processes the stdout to extract both regular output and the result object"""
        try:
            parts = stdout.split('__RESULT_START__')
            if len(parts) < 2: # TODO: Should != 2 but vm_library is returning one more part of __RESULT_START__
                return stdout, {}

            normal_output = parts[0].strip()
            result_part = parts[1].split('__RESULT_END__')[0].strip()

            try:
                result_data = json.loads(result_part) if result_part else {}
            except json.JSONDecodeError:
                result_data = {}

            return normal_output, result_data
        except Exception:
            return stdout, {} 