import subprocess
import tempfile
import os


def run_user_code(code: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Execution timed out"
    finally:
        os.remove(tmp_path)
