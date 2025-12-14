import os
import subprocess
import sys

# 1. Create the entry point wrapper
wrapper_code = """
import sys
import os
import streamlit.web.cli as stcli

def resolve_path(path):
    if getattr(sys, '_MEIPASS', False):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.getcwd(), path)

if __name__ == "__main__":
    script_path = resolve_path("desktop_agent_v2.py")
    sys.argv = ["streamlit", "run", script_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
"""

with open("launcher.py", "w") as f:
    f.write(wrapper_code)

print("🚀 Building EXE... this may take a few minutes.")

# 2. Run PyInstaller
# --onefile: Bundles everything into one .exe
# --noconsole: Hides the black terminal window (optional, keep it for debugging first)
subprocess.check_call([
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--additional-hooks-dir=.",
    "--add-data=desktop_agent_v2.py:.", # Include the main script
    "--collect-all=streamlit",          # Grab all Streamlit dependencies
    "--collect-all=google",             # Grab Google dependencies
    "--collect-all=mss",
    "--clean",
    "launcher.py"
])

print("✅ Build Complete! Check the 'dist' folder for launcher.exe")
