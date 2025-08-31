from flask import Flask, request, jsonify
from .executors import get_executor
import logging
import json
import dotenv

dotenv.load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s   %(name)s  [%(levelname)s]    %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_code():
    """
    API endpoint to execute code using the VMs library
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract parameters
        code = data.get("code", "")
        language = data.get("language", "python")
        dependencies = data.get("dependencies", None)
        inputs = data.get("input", {})
        env_vars = data.get("env", {})
        execution_timeout = data.get("execution_timeout", 360)
        
        logger.info(f"Received execution request for language: {language}")
        logger.info(f"Execution timeout: {execution_timeout}")
        
        # Get executor and execute code
        executor = get_executor(language)
        result = executor.execute(
            code=code,
            language=language,
            dependencies=dependencies,
            inputs=inputs,
            env_vars=env_vars,
            execution_timeout=execution_timeout
        )
        
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        return jsonify({"error": f"ValueError: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return jsonify({"error": f"Error executing code: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "service": "AVM Execution Engine"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
