from .python_executor import PythonExecutor
from .typescript_executor import TypeScriptExecutor
from .php_executor import PHPExecutor

EXECUTORS = {
    "python": PythonExecutor,
    "typescript": TypeScriptExecutor,
    # "php": PHPExecutor
}

def get_executor(language: str):
    executor_class = EXECUTORS.get(language.lower())
    if not executor_class:
        raise ValueError(f"Unsupported language: {language}")
    return executor_class() 