import os
import json
import subprocess
import re
import shutil
from typing import List, Dict, Any
from .base import BaseExecutor

class TypeScriptExecutor(BaseExecutor):
    def __init__(self):
        super().__init__()
        self.npm_path = shutil.which('npm')
        self.npx_path = shutil.which('npx')
        if not self.npm_path or not self.npx_path:
            raise RuntimeError("npm and npx must be installed and available in PATH")

    def get_dependencies(self, code: str) -> List[str]:
        dependencies = set()
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',  # import x from 'y'
            r'import\s+[\'"]([^\'"]+)[\'"]',              # import 'y'
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',   # require('y')
            r'import\s*{\s*.*\s*}\s*from\s*[\'"]([^\'"]+)[\'"]'  # import { x } from 'y'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                dep = match.group(1)
                if not dep.startswith('.') and not dep.startswith('/'):
                    dependencies.add(dep.split('/')[0])
        
        dependencies.update(['typescript', 'ts-node'])
        return list(dependencies)

    def install_dependencies(self, dependencies: List[str], venv_path: str):
        if not dependencies:
            return

        package_json = {
            "dependencies": {dep: "latest" for dep in dependencies},
            "scripts": {
                "start": "ts-node"
            }
        }
        
        tsconfig = {
            "compilerOptions": {
                "target": "es2016",
                "module": "commonjs",
                "esModuleInterop": True,
                "forceConsistentCasingInFileNames": True,
                "strict": True,
                "skipLibCheck": True
            }
        }

        with open(os.path.join(venv_path, "package.json"), "w") as f:
            json.dump(package_json, f)
        
        with open(os.path.join(venv_path, "tsconfig.json"), "w") as f:
            json.dump(tsconfig, f)
        
        subprocess.run([self.npm_path, "install"], cwd=venv_path, check=True)

    def _get_file_extension(self) -> str:
        return ".ts"

    def _prepare_code(self, code: str, inputs: Dict[str, Any], env_vars: Dict[str, str]) -> str:
        """Prepares the TypeScript code by adding input and environment variables"""
        
        env_code = "\n".join([f"process.env['{k}'] = '{v}';" for k, v in env_vars.items()])
        if env_code:
            code = f"{env_code}\n{code}"

        input_declarations = []
        for k, v in inputs.items():
            if isinstance(v, str):
                input_declarations.append(f"const {k}: string = {json.dumps(v)};")
            elif isinstance(v, (int, float)):
                input_declarations.append(f"const {k}: number = {json.dumps(v)};")
            elif isinstance(v, bool):
                input_declarations.append(f"const {k}: boolean = {json.dumps(v)};")
            elif isinstance(v, list):
                input_declarations.append(f"const {k}: any[] = {json.dumps(v)};")
            elif isinstance(v, dict):
                input_declarations.append(f"const {k}: Record<string, any> = {json.dumps(v)};")
            else:
                input_declarations.append(f"const {k}: any = {json.dumps(v)};")

        if input_declarations:
            code = "\n".join(input_declarations) + "\n" + code

        code += """
// Wrapper to manage the result
let result: any = null;
try {
    if (typeof output !== 'undefined') {
        result = output;
    }
} catch (error) {
    console.error('Error capturing result:', error);
}

// Output in JSON format
console.log('__RESULT_START__');
console.log(JSON.stringify(result));
console.log('__RESULT_END__');
"""
        return code

    def _execute_directly(self, code_file_path: str, inputs: Dict[str, Any], env_vars: Dict[str, str]) -> subprocess.CompletedProcess:
        venv_dir = os.path.dirname(code_file_path)
        self.install_dependencies(['typescript', 'ts-node'], venv_dir)
        return self._run_ts_node(code_file_path, venv_dir, env_vars)

    def _execute_with_dependencies(self, code_file_path: str, dependencies: List[str], inputs: Dict[str, Any], env_vars: Dict[str, str]) -> subprocess.CompletedProcess:
        venv_dir = os.path.dirname(code_file_path)
        self.install_dependencies(dependencies, venv_dir)
        return self._run_ts_node(code_file_path, venv_dir, env_vars)

    def _run_ts_node(self, code_file_path: str, venv_dir: str, env_vars: Dict[str, str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [self.npx_path, "ts-node", code_file_path],
            capture_output=True,
            text=True,
            timeout=self.EXECUTION_TIMEOUT,
            cwd=venv_dir,
            env={**os.environ, **env_vars}
        )

    def _process_output(self, stdout: str) -> tuple[str, Dict[str, Any]]:
        """Processes the stdout to extract both regular output and the result object"""
        try:
            parts = stdout.split('__RESULT_START__')
            if len(parts) != 2:
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