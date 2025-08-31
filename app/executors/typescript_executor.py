import json
import re
from typing import List, Dict, Any
from .base import BaseExecutor


class TypeScriptExecutor(BaseExecutor):


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

    def install_dependencies(self, dependencies: List[str]):
        if not dependencies:
            return
        
        for dep in dependencies:
            pass # TODO: Implement npm install by using the vm_library

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