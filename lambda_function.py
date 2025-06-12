import json
from app.main import executor_handler

def handler(event, context):
    # If event is a string, try to parse it as JSON
    if isinstance(event, str):
        try:
            event = json.loads(event)
        except json.JSONDecodeError:
            # If parsing fails, use the string as is
            return executor_handler(event)
    
    # If event is a dict and has a body field, parse the body as JSON
    if isinstance(event, dict) and "body" in event:
        try:
            # The body is a JSON string that needs to be parsed
            body = json.loads(event["body"])
            return executor_handler(body)
        except json.JSONDecodeError:
            # If body parsing fails, use empty dict
            return executor_handler({})
    elif isinstance(event, dict):
        # If it's a dict but no body field, use the event directly
        return executor_handler(event)
    else:
        # For any other type, use as is
        return executor_handler(event)