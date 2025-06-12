from app.main import executor_handler

def handler(event, context):
    return executor_handler(event)