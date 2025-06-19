from flask import Flask, request
import subprocess
import os
import signal
import psutil

app = Flask(__name__)

VENV_PYTHON = os.path.expanduser('~/HawkEye/.venv/bin/python')
SCRIPT_PATH = os.path.expanduser('~/HawkEye/crash_watch_v2.py')

# Store the subprocess.Popen object globally to manage restart
process = None

def start_script():
    global process
    if process is not None and process.poll() is None:
        # Process already running
        return
    process = subprocess.Popen([VENV_PYTHON, SCRIPT_PATH])

def stop_script():
    global process
    if process is None:
        return
    # Try to terminate the process gently
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    process = None

@app.route('/webhook', methods=['POST'])
def webhook():
    # Optional: verify GitHub secret here for security
    # Pull latest changes
    git_pull = subprocess.run(['git', '-C', os.path.expanduser('~/HawkEye'), 'pull'], capture_output=True)
    print(git_pull.stdout.decode())
    print(git_pull.stderr.decode())

    # Restart the crash_watch script
    stop_script()
    start_script()

    return 'Updated', 200

if __name__ == "__main__":
    start_script()
    app.run(host='0.0.0.0', port=5000)
