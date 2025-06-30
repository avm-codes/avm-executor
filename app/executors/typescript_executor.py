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
        import sys
        print(f"[DEBUG] sys.executable: {sys.executable}")
        print(f"[DEBUG] os.environ['PATH']: {os.environ.get('PATH')}")
        self.npm_path = shutil.which('npm')
        self.npx_path = shutil.which('npx')
        print(f"[DEBUG] npm_path: {self.npm_path}")
        print(f"[DEBUG] npx_path: {self.npx_path}")
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

        import os
        import subprocess
        print(f"[DEBUG] venv_path: {venv_path}")
        print(f"[DEBUG] venv_path contents: {os.listdir(venv_path)}")
        print(f"[DEBUG] venv_path permissions: {oct(os.stat(venv_path).st_mode)}")
        try:
            subprocess.run(["ls", "-l", venv_path], check=False)
        except Exception as e:
            print(f"[DEBUG] Could not list venv_path: {e}")

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

        # Set npm/yarn environment to use /tmp for cache and home
        npm_env = {**os.environ, "HOME": "/tmp", "NPM_CONFIG_CACHE": "/tmp/.npm", "NO_UPDATE_NOTIFIER": "1"}
        
        # Configure npm for Lambda environment
        npm_config = [
            "--no-audit",  # Skip audit to speed up installation
            "--no-fund",   # Skip funding message
            "--no-optional",  # Skip optional dependencies
            "--production",   # Only install production dependencies
            "--silent",       # Reduce output
            "--no-update-notifier"  # Suppress update notices (ensure this is last)
        ]
        
        try:
            # First try with npm install
            result = subprocess.run(
                [self.npm_path, "install"] + npm_config, 
                cwd=venv_path, 
                check=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=npm_env
            )
            print(f"npm install successful: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"npm install failed: {e.stderr}")
            # If npm install fails, try with npm ci (clean install)
            try:
                result = subprocess.run(
                    [self.npm_path, "ci"] + npm_config, 
                    cwd=venv_path, 
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=npm_env
                )
                print(f"npm ci successful: {result.stdout}")
            except subprocess.CalledProcessError as e2:
                print(f"npm ci failed: {e2.stderr}")
                # If both fail, try with yarn as fallback
                yarn_path = shutil.which('yarn')
                if yarn_path:
                    try:
                        result = subprocess.run(
                            [yarn_path, "install", "--production", "--silent"],
                            cwd=venv_path,
                            check=True,
                            capture_output=True,
                            text=True,
                            timeout=300,
                            env=npm_env
                        )
                        print(f"yarn install successful: {result.stdout}")
                    except subprocess.CalledProcessError as e3:
                        error_msg = f"Failed to install dependencies with npm and yarn. npm error: {e.stderr}, npm ci error: {e2.stderr}, yarn error: {e3.stderr}"
                        print(error_msg)
                        raise RuntimeError(error_msg)
                else:
                    error_msg = f"Failed to install dependencies with npm. npm error: {e.stderr}, npm ci error: {e2.stderr}"
                    print(error_msg)
                    raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = "npm install timed out after 5 minutes"
            print(error_msg)
            raise RuntimeError(error_msg)

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
    // Use eval to safely check if output variable exists without TypeScript compilation errors
    const outputExists = (() => {
        try {
            return typeof eval('output') !== 'undefined';
        } catch {
            return false;
        }
    })();
    
    if (outputExists) {
        result = (eval('output') as any);
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