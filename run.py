import sys
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    venv_streamlit = root / ".venv" / "Scripts" / "streamlit.exe"
    app_file = root / "src" / "dashboard" / "app.py"

    print("=" * 60)
    print("🏛️ Starting Atlas AQAR Interactive Dashboard...")
    print(f"Target: {app_file}")
    print("URL:    http://localhost:8501")
    print("=" * 60)

    if venv_streamlit.exists():
        cmd = [str(venv_streamlit), "run", str(app_file)]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_file)]

    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\n[!] Dashboard stopped by user.")

if __name__ == "__main__":
    main()
