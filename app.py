import json
import queue
from flask import Flask, request, jsonify
from threading import Thread, Event, Lock
import uuid
import time

from lambda_function import handler

app = Flask(__name__)

# Worker thread control
worker_stop_event = Event()
task_tracker = {
    "isRunning": False,
    "isCompleted": False
}
task_tracker_lock = Lock()
task_queue = queue.Queue()
result_queue = queue.Queue()

def start_execution():
    with task_tracker_lock:
        task_tracker["isRunning"] = True
        task_tracker["isCompleted"] = False

def stop_execution():
    with task_tracker_lock:
        task_tracker["isRunning"] = False
        task_tracker["isCompleted"] = True

def get_execution_status():
    with task_tracker_lock:
        task_status = task_tracker.copy()
        task_tracker["isCompleted"] = False
    return task_status

def worker():
    while not worker_stop_event.is_set():
        data = task_queue.get()
        result = handler(data, None)
        result_queue.put(result)
        stop_execution()

@app.route('/exec/sync', methods=['POST'])
def exec_sync():
    data = request.json
    start_execution()
    result = handler(json.dumps(data), None)
    stop_execution()
    return jsonify(result)

@app.route('/exec/async', methods=['POST'])
def exec_async():
    data = request.json
    start_execution()
    task_queue.put(data)
    return jsonify({"success": True})

@app.route('/exec/result', methods=['POST'])
def exec_result():
    try:
        result = result_queue.get(timeout=2)  # Wait for a result
        return jsonify(result)
    except queue.Empty:
        return jsonify({"error": "No result available"}), 404

@app.route('/exec/status', methods=['POST'])
def exec_status():
    status = get_execution_status()
    return jsonify(status)

if __name__ == '__main__':
    # Start worker thread
    Thread(target=worker, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)