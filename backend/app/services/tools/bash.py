import subprocess
from app.services.config import WORKSPACE_DIR


ALLOWED_PREFIXES = [
    "ls",
    "pwd",
    "tree",
    "find",
    "grep",
    "npm install",
    "npm run dev",
    "npm run build",
    "npm create vite@latest"
]

def run_command(command):

    if not any(command.startswith(x) for x in ALLOWED_PREFIXES):
        raise Exception("Command not allowed")

    result = subprocess.run(
        command,
        shell=True,
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
    