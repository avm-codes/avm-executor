from .executors import get_executor
from .executors.base import BaseExecutor
import logging
import json
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s   %(name)s  [%(levelname)s]    %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def executor_handler(payload):
    
    input_data = payload
    if not input_data:
        raise ValueError("No json input received in PAYLOAD env var. Exit.")
    
    code = input_data.get("code", "")
    language = input_data.get("language", "python")
    dependencies = input_data.get("dependencies", None)
    inputs = input_data.get("input", {})
    env_vars = input_data.get("env", {})
    execution_timeout=input_data.get("execution_timeout", BaseExecutor.EXECUTION_TIMEOUT)
    logger.info(f"Execution timeout: {execution_timeout}")
    try:
        executor = get_executor(language)
        result = executor.execute(
            code=code,
            dependencies=dependencies,
            inputs=inputs,
            env_vars=env_vars,
            execution_timeout=execution_timeout
        )
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result)
        }
        return response
    except ValueError as e:
        raise ValueError(f"ValueError: {str(e)}")
    except Exception as e:
        raise Exception(f"Error executing code: {str(e)}")
