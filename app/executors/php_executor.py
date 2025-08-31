# PHP Executor - TEMPORARILY DISABLED
# 
# This file has been commented out to disable PHP support.
# All code is preserved and can be uncommented when needed.
#
# import os
# import re
# import shutil
# import subprocess
# import json
# from typing import List, Dict, Any
# from .base import BaseExecutor
#
# class PHPExecutor(BaseExecutor):
#     
#     def __init__(self):
#         super().__init__()
#         self.php_path = shutil.which('php')
#         self.composer_path = shutil.which('composer')
#         if not self.php_path:
#             raise RuntimeError("PHP is not installed or not available in PATH")
#
#     def get_dependencies(self, code: str) -> List[str]:
#         """Analyzes PHP code to extract Composer package dependencies."""
#         dependencies = set()
#         patterns = [
#             r'use\s+([a-zA-Z0-9_\\\\]+);',
#             r'require[_once]*\s*\(\s*[\'\"]([^\'\"/][^\'\"]+)[\'\"]\s*\)',
#             r'include[_once]*\s*\(\s*[\'\"]([^\'\"/][^\'\"]+)[\'\"]\s*\)'
#         ]
#         composer_pattern = re.compile(r'^[a-z0-9]([_.-]?[a-z0-9]+)*/[a-z0-9]([_.-]?[a-z0-9]+)*$', re.IGNORECASE)
#         
#         for pattern in patterns:
#             matches = re.finditer(pattern, code)
#             for match in matches:
#                 dep = match.group(1)
#                 # Check if it matches Composer package format (vendor/package)
#                 if composer_pattern.match(dep):
#                     dependencies.add(dep)
#         
#         return list(dependencies)
#
#     def install_dependencies(self, dependencies: List[str], venv_path: str):
#         if not dependencies or not self.composer_path:
#             return
#         
#         composer_json = {
#             "require": {dep: "*" for dep in dependencies}
#         }
#         
#         with open(os.path.join(venv_path, "composer.json"), "w") as f:
#             json.dump(composer_json, f)
#
#         subprocess.run([self.composer_path, "install", "--no-dev"], cwd=venv_path, check=True)
#
#     def _get_file_extension(self) -> str:
#         return ".php"
#
#     def _prepare_code(self, code: str, inputs: Dict[str, Any], env_vars: Dict[str, str]) -> str:
#         """Prepares the PHP code by adding input and environment variables"""
#         
#         env_code = "\n".join([f"$_ENV['{k}'] = '{v}';" for k, v in env_vars.items()])
#         if env_code:
#             code = f"<?php\n{env_code}\n{code}"
#         else:
#             code = f"<?php\n{code}"
#
#         input_declarations = []
#         for k, v in inputs.items():
#             if isinstance(v, str):
#                 input_declarations.append(f"${k} = '{v}';")
#             elif isinstance(v, (int, float)):
#                 input_declarations.append(f"${k} = {v};")
#             elif isinstance(v, bool):
#                 input_declarations.append(f"${k} = " + ("true" if v else "false") + ";")
#             elif isinstance(v, list):
#                 input_declarations.append(f"${k} = " + json.dumps(v) + ";")
#             elif isinstance(v, dict):
#                 input_declarations.append(f"${k} = " + json.dumps(v) + ";")
#             else:
#                 input_declarations.append(f"${k} = " + json.dumps(v) + ";")
#
#         if input_declarations:
#             code = code.replace("<?php\n", "<?php\n" + "\n".join(input_declarations) + "\n")
#
#         code += """
# // Wrapper to manage the result
# $result = null;
# try {
#     if (isset($output)) {
#         $result = $output;
#     }
# } catch (Exception $e) {
#     error_log('Error capturing result: ' . $e->getMessage());
# }
#
# // Output in JSON format
# echo "__RESULT_START__\n";
# echo json_encode($result) . "\n";
# echo "__RESULT_END__\n";
# """
#         return code
#
#     def _execute_directly(self, code_file_path: str, inputs: Dict[str, Any], env_vars: Dict[str, str], execution_timeout: int) -> subprocess.CompletedProcess:
#         return subprocess.run(
#             [self.php_path, code_file_path],
#             capture_output=True,
#             text=True,
#             timeout=execution_timeout,
#             env={**os.environ, **env_vars}
#         )
#
#     def _execute_with_dependencies(self, code_file_path: str, dependencies: List[str], inputs: Dict[str, Any], env_vars: Dict[str, str], execution_timeout: int) -> subprocess.CompletedProcess:
#         venv_dir = os.path.dirname(code_file_path)
#         self.install_dependencies(dependencies, venv_dir)
#         
#         return subprocess.run(
#             [self.php_path, code_file_path],
#             capture_output=True,
#             text=True,
#             timeout=execution_timeout,
#             cwd=venv_dir,
#             env={**os.environ, **env_vars}
#         )
#
#     def _process_output(self, stdout: str) -> tuple[str, Dict[str, Any]]:
#         """Processes the stdout to extract both regular output and the result object"""
#         try:
#             parts = stdout.split('__RESULT_START__')
#             if len(parts) != 2:
#                 return stdout, {}
#
#             normal_output = parts[0].strip()
#             result_part = parts[1].split('__RESULT_END__')[0].strip()
#
#             try:
#                 result_data = json.loads(result_part) if result_part else {}
#             except json.JSONDecodeError:
#                 result_data = {}
#
#             return normal_output, result_data
#         except Exception:
#             return stdout, {}